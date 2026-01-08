/** * ===================================================================
 * main js - HernandezPalo Portfolio (Recurrent Animation Edition)
 * =================================================================== 
 */ 

(function($) {

    "use strict";

    /*---------------------------------------------------- */
    /* Preloader
    ------------------------------------------------------ */ 
   $(window).load(function() {
        $("#loader").fadeOut("slow", function(){
            $("#preloader").delay(300).fadeOut("slow");
        });       
    });

    /*---------------------------------------------------- */
    /* FitText Settings
    ------------------------------------------------------ */
    setTimeout(function() {
        $('#intro h1').fitText(1, { minFontSize: '42px', maxFontSize: '84px' });
    }, 100);

    /*---------------------------------------------------- */
    /* FitVids
    ------------------------------------------------------ */ 
    $(".fluid-video-wrapper").fitVids();

    /*---------------------------------------------------- */
    /* Owl Carousel
    ------------------------------------------------------ */ 
    $("#owl-slider").owlCarousel({
        navigation: false,
        pagination: true,
        itemsCustom : [[0, 1], [700, 2], [960, 3]],
        navigationText: false
    });

    /*----------------------------------------------------- */
    /* Alert Boxes
    ------------------------------------------------------- */
    $('.alert-box').on('click', '.close', function() {
      $(this).parent().fadeOut(500);
    }); 

    /*----------------------------------------------------- */
    /* Stat Counter (Impact Metrics) - RECURRENTE
    ------------------------------------------------------- */
   var statSection = $("#impact-metrics"),
       stats = $(".animate-num");

   if (statSection.length > 0) {
       statSection.waypoint({
        handler: function(direction) {
            if (direction === "down") {             
                   stats.each(function () {
                       var $this = $(this);
                       var target = $this.data('target'); 

                       $({ Counter: 0 }).animate({ Counter: target }, {
                            duration: 2500,
                            easing: 'swing',
                            step: function (curValue) {
                                $this.text(Math.ceil(curValue));
                            }
                        });
                    });
            } else if (direction === "up") {
                // Resetear a 0 cuando el usuario sube para que pueda volver a animarse
                stats.text('0');
            }
        },
        offset: "85%"
    }); 
   }

/*----------------------------------------------------- */
    /* Skill Bars Animation (About Section) - RECURRENTE
    ------------------------------------------------------- */
    var aboutSection = $("#about"),
        skillBars = $(".skill-bars .progress");

    if (aboutSection.length > 0) {
        aboutSection.waypoint({
            handler: function(direction) {
                if (direction === "down") {
                    skillBars.each(function() {
                        var $this = $(this);
                        var percent = $this.data('percent');
                        
                        // Pequeño delay para asegurar que el navegador note el cambio
                        setTimeout(function(){
                            $this.css("width", percent);
                        }, 100);
                    });
                } else if (direction === "up") {
                    // Resetear el ancho a 0 al subir para que esté listo para la próxima vez
                    skillBars.css("width", "0%");
                }
            },
            offset: "90%" // Lo activamos un poco más tarde para asegurar que se vea
        });
    }

    /*---------------------------------------------------- */
    /* Masonry
    ------------------------------------------------------ */
    var containerProjects = $('#folio-wrapper');
    containerProjects.imagesLoaded( function() {
        containerProjects.masonry( {          
            itemSelector: '.folio-item',
            resize: true 
        });
    });

    /*----------------------------------------------------*/
    /* Modal Popup
    ------------------------------------------------------*/
   $('.item-wrap a').magnificPopup({
      type:'inline',
      fixedContentPos: false,
      removalDelay: 300,
      showCloseBtn: false,
      mainClass: 'mfp-fade'
   });

   $(document).on('click', '.popup-modal-dismiss', function (e) {
    e.preventDefault();
    $.magnificPopup.close();
   });
    
    /*-----------------------------------------------------*/
    /* Navigation Menu
   ------------------------------------------------------ */  
   var toggleButton = $('.menu-toggle'),
       nav = $('.main-navigation');

   toggleButton.on('click', function(e) {
        e.preventDefault();
        toggleButton.toggleClass('is-clicked');
        nav.slideToggle();
    });

    nav.find('li a').on("click", function() {   
        toggleButton.toggleClass('is-clicked'); 
        nav.fadeOut();          
    });

   /*---------------------------------------------------- */
    /* Highlight the current section in the navigation bar
    ------------------------------------------------------ */
    var sections = $("section"),
    navigation_links = $("#main-nav-wrap li a");    

    sections.waypoint( {
       handler: function(direction) {
           var active_section;
            active_section = $('section#' + this.element.id);
            if (direction === "up") active_section = active_section.prev();
            var active_link = $('#main-nav-wrap a[href="#' + active_section.attr("id") + '"]');         
            navigation_links.parent().removeClass("current");
            active_link.parent().addClass("current");
        }, 
        offset: '25%'
    });

    /*---------------------------------------------------- */
    /* Smooth Scrolling
    ------------------------------------------------------ */
    $('.smoothscroll').on('click', function (e) {
        e.preventDefault();
        var target = this.hash,
            $target = $(target);

        $('html, body').stop().animate({
            'scrollTop': $target.offset().top
        }, 800, 'swing', function () {
            window.location.hash = target;
        });
    });  
  
   /*---------------------------------------------------- */
    /* Placeholder Plugin Settings
    ------------------------------------------------------ */ 
    $('input, textarea, select').placeholder()  

    /*---------------------------------------------------- */
    /* Contact Form
    ------------------------------------------------------ */
    if($('#contactForm').length > 0) {
        $('#contactForm').validate({
            submitHandler: function(form) {
                var sLoader = $('#submit-loader');
                $.ajax({        
                  type: "POST",
                  url: "inc/sendEmail.php",
                  data: $(form).serialize(),
                  beforeSend: function() { sLoader.fadeIn(); },
                  success: function(msg) {
                    if (msg == 'OK') {
                        sLoader.fadeOut(); 
                        $('#message-warning').hide();
                        $('#contactForm').fadeOut();
                        $('#message-success').fadeIn();   
                    } else {
                        sLoader.fadeOut(); 
                        $('#message-warning').html(msg);
                        $('#message-warning').fadeIn();
                    }
                  },
                  error: function() {
                    sLoader.fadeOut(); 
                    $('#message-warning').html("Something went wrong. Please try again.");
                    $('#message-warning').fadeIn();
                  }
              });           
            }
        });
    }

    /*----------------------------------------------------- */
    /* Back to top
   ------------------------------------------------------- */ 
    var pxShow = 300; 
    var fadeInTime = 400; 
    var fadeOutTime = 400; 

    jQuery(window).scroll(function() {
        if (!( $("#header-search").hasClass('is-visible'))) {
            if (jQuery(window).scrollTop() >= pxShow) {
                jQuery("#go-top").fadeIn(fadeInTime);
            } else {
                jQuery("#go-top").fadeOut(fadeOutTime);
            }
        }       
    });     

})(jQuery);