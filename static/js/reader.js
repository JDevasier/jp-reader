$(document).ready(function() {
    let last_text_update = Date.now()
    // let jp_input_timeout = null
    let prev_input = "";

    $("#jp-input").on("paste keyup change", function(e) {
        let input_text = $("#jp-input").val().replaceAll("\n", "");
        if (input_text == "" || input_text == prev_input) {
            return
        }

        // $("#jp-input").prop( "disabled", true );

        $.ajax({
            type: "POST",
            contentType: "application/json",
            url: "/parse_jp", 
            data: JSON.stringify({"text":$("#jp-input").val()}),
            success: (data) => { 
                populate_page($("#vocab-list"), $("#content-area"), data, $("#jp-input").val());
                // $("#jp-input").prop( "disabled", false );
            },
            error: (data) => {
                // $("#jp-input").prop( "disabled", false );
            }
        });
        prev_input = input_text
    });

    function populate_page(vocab_el, content_el, data, query_text) {
        // vocab_el: json element, i.e., $("#vocab-list")
        // vocab: json dictionary, i.e., [{"私": "I, Me"}]
        
        // populate content
        content_el.empty();
        content_el.append(data["content"]);

        vocab = data["vocab"];
        
        // populate vocab
        if (vocab != null && vocab.length != 0) {
            vocab.sort(function(a,b) {
                return b.jlpt - a.jlpt;
            });

            vocab_el.empty();

            let last_jlpt = vocab[0].jlpt;
            vocab_el.append("<h4>JLPT N"+last_jlpt+"</h4>");
            vocab_el.append("<div class='jlpt"+last_jlpt+"'>");

            vocab.forEach(voc => {
                let vocab_id = "vocab-" + voc.word.replace("~", "");
                
                if (voc.jlpt !== last_jlpt) {
                    vocab_el.append("</div>");
                    last_jlpt = voc.jlpt;
                    if (last_jlpt == 0) {
                        vocab_el.append("<h4>Unknown</h4>");
                    } else {
                        vocab_el.append("<h4>JLPT N"+last_jlpt+"</h4>");
                    }
                    
                    vocab_el.append("<div>");
                }

                if (voc.eng.length == 0) {
                    vocab_el.append("<p class='vocab-list-word'><a class='vocab-kanji' id='"+vocab_id+"'>"+voc.word+"</a>("+voc.pron+"): (unk)</p>");
                } else {
                    vocab_el.append("<p class='vocab-list-word'><a class='vocab-kanji' id='"+vocab_id+"'>"+voc.word+"</a>("+voc.pron+"): "+voc.eng[0]+"</p>");
                }
            });
            vocab_el.append("</div>")
        }

        let cur_timeout = null

        $(".vocab-word").prop("onclick", null).off("click");
        $(".vocab-word").click(function(e) {
            let word = $(e.target).text().replace("~", "");

            $("#vocab-"+word)[0].scrollIntoView({behavior: "smooth", block: "center"})
            $("#vocab-"+word).parent("p").css("background-color", "rgba(255, 127, 80, 0.5)");
            
            $("#vocab-"+word).parent("p").stop().animate({
                backgroundColor: "#FFFFFF00"
            }, 5000)
        });
    }
})

