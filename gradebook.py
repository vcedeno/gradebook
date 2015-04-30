import pkg_resources
import requests

from urlparse import urlparse

from xblock.core import XBlock
from xblock.fields import Scope, Integer, String
from xblock.fragment import Fragment
from courseware.models import StudentModule
from submissions import api as submissions_api
from submissions.models import StudentItem
from student.models import anonymous_id_for_user, UserProfile

class GradeBookBlock(XBlock):
    """
    An XBlock providing oEmbed capabilities for video (currently only supporting Vimeo)
    """
    has_score = True
    href = String(help="URL of the video page at the provider", default=None, scope=Scope.content)
    maxwidth = Integer(help="Maximum width of the video", default=800, scope=Scope.content)
    maxheight = Integer(help="Maximum height of the video", default=450, scope=Scope.content)
    watched_count = Integer(help="The number of times the student watched the video", default=0, scope=Scope.user_state)

	

    def student_view(self, context):
        """
        Create a fragment used to display the XBlock to a student.
        `context` is a dictionary used to configure the display (unused)
        Returns a `Fragment` object specifying the HTML, CSS, and JavaScript
        to display.
        """
        provider, embed_code = self.get_embed_code_for_url(self.href)
		
        # Load the HTML fragment from within the package and fill in the template
        html_str = pkg_resources.resource_string(__name__, "static/html/gradebook.html")
        frag = Fragment(unicode(html_str).format(self=self, embed_code=embed_code))

        # Load CSS
        css_str = pkg_resources.resource_string(__name__, "static/css/gradebook.css")
        frag.add_css(unicode(css_str))

        # Load JS
        if provider == 'vimeo.com':
            # Load the Froogaloop library from vimeo CDN.
            frag.add_javascript_url("//f.vimeocdn.com/js/froogaloop2.min.js")
            js_str = pkg_resources.resource_string(__name__, "static/js/gradebook.js")
            frag.add_javascript(unicode(js_str))
            frag.initialize_js('GradeBookBlock')


        return frag

    def studio_view(self, context):
        """
        Create a fragment used to display the edit view in the Studio.
        """
        html_str = pkg_resources.resource_string(__name__, "static/html/gradebook_edit.html")
        href = self.href or ''
        frag = Fragment(unicode(html_str).format(href=href, maxwidth=self.maxwidth, maxheight=self.maxheight))

        js_str = pkg_resources.resource_string(__name__, "static/js/gradebook_edit.js")
        frag.add_javascript(unicode(js_str))
        frag.initialize_js('GradeBookEditBlock')

        return frag

    def get_embed_code_for_url(self, url):
        """
        Get the code to embed from the oEmbed provider
        """
        hostname = url and urlparse(url).hostname
        params = {
            'url': url,
            'format': 'json',
            'maxwidth': self.maxwidth,
            'maxheight': self.maxheight
        }

        # Check that the provider is supported
        if hostname == 'vimeo.com':
            oembed_url = 'http://vimeo.com/api/oembed.json'
            params['api'] = True
        else:
            return hostname, '<p>Unsupported video provider ({0})</p>'.format(hostname)

        try:
            r = requests.get(oembed_url, params=params)
            r.raise_for_status()
        except Exception as e:
            return hostname, '<p>Error getting video from provider ({error})</p>'.format(error=e)
        response = r.json()

        return hostname, response['html']

    @XBlock.json_handler
    def studio_submit(self, data, suffix=''):
        """
        Called when submitting the form in Studio.
        """
        self.href = data.get('href')
        self.maxwidth = data.get('maxwidth')
        self.maxheight = data.get('maxheight')

        return {'result': 'success'}

    @XBlock.json_handler
    def mark_as_watched(self, data, suffix=''):  # pylint: disable=unused-argument
        """
        Called upon completion of the video
        """
        if data.get('watched'):
            self.watched_count += 1

        return {'watched_count': self.watched_count}


	def staff_grading_data(self):
		def get_student_data(module):
			state = json.loads(module.state)
			return {
				'module_id': module.id,
				'username': module.student.username,
				'fullname': module.student.profile.name,
				'filename': state.get("uploaded_filename"),
				'timestamp': state.get("uploaded_timestamp"),
				'published': state.get("score_published"),
				'score': state.get("score"),
				'annotated': state.get("annotated_filename"),
				'comment': state.get("comment", ''),
			}
		query = StudentModule.objects.filter(
			course_id=self.xmodule_runtime.course_id,
			module_state_key=self.location.url())
		return {
			'assignments': [get_student_data(module) for module in query],
			'max_score': self.max_score(),
		}
        
    @XBlock.handler
    def enter_grade(self, request, suffix=''):
        #assert self.is_course_staff()
        module = StudentModule.objects.get(pk=request.params['module_id'])
        state = json.loads(module.state)
        state['score'] = watched_count
        state['score_published'] = True    # see student_view
        module.state = json.dumps(state)

        # This is how we'd like to do it.  See student_view
        self.runtime.publish(self, 'grade', {
            'value': state['score'],
            'max_value': 100,
            'user_id': module.student.id
        })

        module.save()
        return Response(json_body=self.staff_grading_data())

    @staticmethod
    def workbench_scenarios():
        """A canned scenario for display in the workbench."""
        return [
            ("grade book",
            """\
                <vertical_demo>
                    <gradebook href="https://vimeo.com/46100581" maxwidth="800" />
                    <html_demo><div>Rate the video:</div></html_demo>
                    <thumbs />
                </vertical_demo>
             """)
        ]