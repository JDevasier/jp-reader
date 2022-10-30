$(document).ready(function() {
    let last_text_update = Date.now()
    // let jp_input_timeout = null

    $("#jp-input").on("paste keyup change", function(e) {
        if ($("#jp-input").val().replaceAll("\n", "") == "") {
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
    });

    function populate_page(vocab_el, content_el, vocab, query_text) {
        // vocab_el: json element, i.e., $("#vocab-list")
        // vocab: json dictionary, i.e., [{"私": "I, Me"}]
        
        // populate content
        content_el.empty();
        let content_html = "<p class='jp-text content-text'>" + query_text + "</p>";
        content_html = content_html.replaceAll("\n", "</p> <p class='jp-text content-text'>");

        // populate vocab
        if (vocab != null && vocab.length != 0) {
            vocab.sort(function(a,b) {
                return b.jlpt - a.jlpt
            });

            vocab_el.empty();

            let last_jlpt = vocab[0].jlpt;
            vocab_el.append("<h4>JLPT N"+last_jlpt+"</h4>");
            vocab_el.append("<div class='jlpt"+last_jlpt+"'>")

            vocab.forEach(voc => {
                if (voc.jlpt !== last_jlpt) {
                    vocab_el.append("</div>")
                    last_jlpt = voc.jlpt
                    if (last_jlpt == 0) {
                        vocab_el.append("<h4>Unknown</h4>");
                    } else {
                        vocab_el.append("<h4>JLPT N"+last_jlpt+"</h4>");
                    }
                    
                    vocab_el.append("<div>")
                }

                if (voc.eng.length == 0) {
                    vocab_el.append("<p class='vocab-list-word'><a class='vocab-kanji'>"+voc.word+"</a> (unk)</p>");
                } else {
                    vocab_el.append("<p class='vocab-list-word'><a class='vocab-kanji'>"+voc.word+"</a>: "+voc.eng+"</p>");
                }

                if (voc.jlpt > 0) {
                    content_html = content_html.replaceAll(voc.word, "<a class='vocab-word'>"+voc.word+"</a>")
                }
                
                
            });
            vocab_el.append("</div>")


        }

        content_el.append(content_html);
    }
})

