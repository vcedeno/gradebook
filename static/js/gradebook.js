function GradeBookBlock(runtime, element) {
    var iframe = $('.gradebook iframe'),
        player = $f(iframe[0]),
        watched_status = $('.gradebook .status .watched-count');

    function on_finish(id) {
        $.ajax({
            type: "POST",
            url: runtime.handlerUrl(element, 'mark_as_watched'),
            data: JSON.stringify({watched: true}),
            success: function(result) {
                watched_status.text(result.watched_count);
            }
        });
		$.post(runtime.handlerUrl(element, 'enter_grade'), form.serialize()).success();
  
    }

    player.addEvent('ready', function() {
        player.addEvent('finish', on_finish);
    });
    
    
}

$(document).ready(function() {
var json = {"items": [
 {"chapter": "Introduction",
  "sections":
 		[{ "name": "Introduction to data 1", "grade":"0"},{ "name": "Introduction to data 2", "grade":"0"}
 		]
 },
  {"chapter": "Linked Lists",
  "sections":
 		[{ "name": "Exercise 1", "grade":"0"}
 		]
  }
]};

var news = document.getElementsByClassName("container")[0];
var items = json.items;
var n= items.length;
$("#sections").text(n + " Sections - Grade: ");

for(var i = 0; i < n; i++) {

var hash = i;
    var $template = $(".template");
	
    var $newPanel = $template.clone();
    $newPanel.find(".collapse").removeClass("in");
    $newPanel.find(".accordion-toggle").attr("href",  "#" + (++hash)).text(" " + items[i].chapter);
     
    var items2 = items[i].sections;
    for(var j = 0; j < items2.length; j++) 
    {	
    	$newPanel.find(".panel-collapse").attr("id", hash).text(items2[j].name + " Grade: " +items2[j].grade);
    	
    }
    $("#accordion").append($newPanel.fadeIn());
}
 });
