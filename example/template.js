//Copyright Matthew Pottage 2015.
// Written primarily to provide a slideshow for the photo albums.
// Depends on styles set in template.css for showing/hiding buttons.
"use strict";

var inSlideshow = false;
var delay = 10;
var currentTimeoutId = 0;
var controls = {
    holder: null,
    next: null,
    previous: null,
    toggleSlideshow: null,
    setDelay: null
};

//Creates the slideshow controls and inserts them.
// innerHTML is set with content for screen readers, hidden via CSS.
function addSlideshowButtons() {
    //Toggle
    controls.toggleSlideshow = document.createElement("button");
    controls.toggleSlideshow.id = "toggle-slideshow";
    controls.toggleSlideshow.onclick = function() {
        inSlideshow = !inSlideshow;
        refreshState();
    };
    //Change duration
    controls.setDelay = document.createElement("input");
    controls.setDelay.id = "set-slideshow-delay";
    controls.setDelay.type = "number";
    controls.setDelay.max = "999";
    controls.setDelay.min = "1";
    controls.setDelay.onchange = function() {
        if (!controls.setDelay.value.match(/^\d+$/))
            controls.setDelay.value = delay;
        else
            changeDelay(controls.setDelay.value);
        refreshState();
    };
    var setDelayLabel = document.createElement("label");
    setDelayLabel.innerHTML = "Delay ";
    setDelayLabel.id = "set-slideshow-delay-label";
    setDelayLabel.htmlFor = "set-slideshow-delay";
    setDelayLabel.appendChild(controls.setDelay);
    controls.holder.insertBefore(controls.toggleSlideshow,controls.next);
    controls.holder.insertBefore(setDelayLabel,controls.next);
}
//Updates the controls to reflect current state (hiding & changing values)
function updateControls() {
    if (inSlideshow) {
        controls.next.hash = controls.previous.hash = "#slideshow="+delay;
        controls.toggleSlideshow.title = "End slideshow";
        controls.toggleSlideshow.innerHTML = "<span>End slideshow</span>";
        controls.setDelay.value = delay;
        controls.setDelay.disabled = false;

        controls.holder.classList.add("slideshow");
    }
    else {
        controls.next.hash = controls.previous.hash = "";
        controls.toggleSlideshow.title = "Start slideshow";
        controls.toggleSlideshow.innerHTML = "<span>Start slideshow</span>";
        controls.setDelay.disabled = true;

        controls.holder.classList.remove("slideshow");
    }
}

//Used to prevent infinite looping between updateFromHash and updateHash()
var lastHashDelay = null; var lastHashSlideshow = null;
var slideshowHash = /^#slideshow=(\d+)$/;

//Alters delay from hash, doesn't refresh.
function updateFromHash() {
    var match = window.location.hash.match(slideshowHash);
    if(match) {
        inSlideshow = true;
        changeDelay(parseInt(match[1]));
    }
    else
        inSlideshow = false;
    lastHashDelay = delay; lastHashSlideshow = inSlideshow;
}
//Updates the hash to reflect the current delay, no refresh.
function updateHash() {
    if(inSlideshow!=lastHashSlideshow || delay!=lastHashDelay) {
        var newHash = "";
        if(inSlideshow)
            newHash = "#slideshow="+delay;
        else
            newHash = "#noslideshow";
        //If there has been no slideshow running, create a new history entry,
        // otherwise replace the current hash with the new one (without creating
        // an entry) - where possible (e.g. not in IE 9).
        if(window.location.hash=="#" || window.location.hash=="" ||
                !window.history.replaceState)
            window.location.hash = newHash;
        else
            window.history.replaceState(null, "", newHash);
        lastHashDelay = delay; lastHashSlideshow = inSlideshow;
    }
}

//Alters delay if newValue is valid, no refresh.
function changeDelay(newValue) {
    if(newValue>0 && newValue<1000)
        delay = newValue;
}

//Cancels the current delay timeout (if any) and starts a new one, if the
// slideshow is running.
function refreshDelay() {
    if(currentTimeoutId) {
        clearTimeout(currentTimeoutId);
        currentTimeoutId = null;
    }
    if(inSlideshow) {
        currentTimeoutId =
            setTimeout(function(){window.location=controls.next.href;},
                    delay*1000);
    }
}

function refreshState() {
    refreshDelay();
    updateControls();
    updateHash();
}

var uiElements = {
    bar: null,
    location: null,
    image: null,
    caption: null,
    toggleLocation: null /*In uiElements as only affects visual appearance*/
};

//VISUAL APPEARANCE CODE FOLLOWS
// Does responsive layouts that cannot be done with CSS, and scrolls to focus on
// albums.

//Scrolls down to the albums-bar (called onload and onhashchange)
function scrollBar() {
    uiElements.bar.scrollIntoView();
}

// Adjusts the #albums-bar#location and #main-image so that they properly fit
// the screen.
function resizeImageToFit() {
    //Resize image to fit, limiting to appropriate height, note that is is after
    // adjustLocationBar(). Ensures that both the image and caption are onscreen.
    var spareHeight = window.innerHeight;
    var imageRect = uiElements.image.getBoundingClientRect();
    spareHeight -= imageRect.top - uiElements.bar.getBoundingClientRect().top;
    spareHeight -= uiElements.caption.getBoundingClientRect().bottom-imageRect.bottom;
    uiElements.image.style.maxHeight = spareHeight+"px";
}

//Hide full image location on albums-bar if the controls are pushed onto the next line.
//Blocks transitions if the page is loading (determined by parameter isOnLoad).
var openLocationAt = 0;
function adjustLocationBar(isOnLoad) {
    if(!uiElements.location.classList)
        return; //classList not supported, and collapsing uses it.
    if (isAddrLarge()) {
        if(!uiElements.toggleLocation) {
            uiElements.location.style.whiteSpace = "nowrap";
            controls.holder.style.whiteSpace = "nowrap";
            openLocationAt = uiElements.location.getBoundingClientRect().width
                +controls.holder.getBoundingClientRect().width;
            uiElements.location.style.whiteSpace = "";
            controls.holder.style.whiteSpace = "";
            if(isOnLoad) //Blocking transitions
                uiElements.location.classList.add("no-transitions");
            uiElements.location.classList.add("collapsed");
            if(isOnLoad) { //Blocking transitions, see WWW.
                getComputedStyle(document.querySelector(
                        "#location ol li")).display; //Forces browser to read style.
                uiElements.location.classList.remove("no-transitions");
            }
            var locationItem = uiElements.location.querySelector("ol li");
            uiElements.toggleLocation = document.createElement("button");
            uiElements.toggleLocation.title = "Show/hide full location";
            uiElements.toggleLocation.innerHTML = "<span>Show/hide full location</span>";
            uiElements.toggleLocation.id = "toggle-full-location";
            uiElements.toggleLocation.onclick = function() {
                uiElements.location.classList.toggle("collapsed");
                uiElements.location.classList.toggle("expanded");
            };
            locationItem.appendChild(uiElements.toggleLocation);
       }
    }
    //Window has been enlarged, the address might now fit.
    else if(uiElements.toggleLocation &&
            uiElements.bar.getBoundingClientRect().width>openLocationAt) {
        uiElements.location.classList.remove("collapsed");
        uiElements.location.classList.remove("expanded");
        uiElements.toggleLocation.parentNode.removeChild(uiElements.toggleLocation);
        uiElements.toggleLocation = null;
    }
}

function isAddrLarge() {
    return uiElements.location.getBoundingClientRect().top!=
        controls.holder.getBoundingClientRect().top;
}
//END VISUAL APPEARANCE CODE

//Limits activating the slideshow to when viewing an image (online
// or offline, when testing images)
if (window.location.pathname.match(/.*\.(jpg|JPG|png|svg)(\.html)?$/)
        ||window.location.search.match(/.*\.(jpg|JPG|png|svg)$/)) {
    document.addEventListener("DOMContentLoaded", function() {
        controls.next = document.querySelector(".view a.next");
        controls.previous = document.querySelector(".view a.previous");
        controls.holder = controls.next.parentNode;
        uiElements.image = document.querySelector("figure.large-image img");
        uiElements.caption = document.querySelector("figure.large-image figcaption");
        uiElements.bar = document.querySelector("header.view");
        uiElements.location = document.querySelector("nav.view");
        addSlideshowButtons();
        updateFromHash();
        updateControls(); //Make controls reflect settings from hash.
    }, false);
    window.addEventListener("load", function() {
        adjustLocationBar(true);
        resizeImageToFit();
        scrollBar(); //Focus on image.
        refreshDelay(); //Start the delay when everything is loaded.
    }, false);
    window.addEventListener("hashchange", function() {
        scrollBar(); //Focus attention on image.
        updateFromHash(); //Get new slideshow status
        refreshState(); //Apply changes
    }, false);
    window.onresize = function() {
        resizeImageToFit();
        adjustLocationBar();
    };
}
//Not viewing an image, add a slideshow link for the folder if it has any images as
// direct children.
else {
    document.addEventListener("DOMContentLoaded", function() {
        var firstImage = document.querySelector(
                "figure.view.thumbnails figure:not(.folder) a");
        if(firstImage) {
            var btnHolder = document.createElement("div");
            btnHolder.classList.add("controls");
            btnHolder.innerHTML = "<a href='"+firstImage.pathname+"#slideshow="
                +delay+"'"+ "id='toggle-slideshow' title='Start Slideshow'>"
                +"<span>Start Slideshow</span></a>";
            document.querySelector("header.view").appendChild(btnHolder);
        }
    }, false);
}
