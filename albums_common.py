#!/usr/bin/python3

# Copyright Matthew Pottage 2014
# Produces photo albums for a website, based on the directory hierachy of a
# specified directory.
# Security Assumptions: Attacker has direct or indirect access to script via http/https,
#   can edit files inside document_root (excluding the albums code and directory) via sftp.

# Script protects against accessing files outside of the document root by two
# methods.
# 1. Checks that the real path of all files accessed starts with the real path
#       of the document root, i.e. No symlinks to outside the root.
# 2. Rejects any queries (query_path) paths that contain "../", "~" "/.".
#       This blocks navigation outside the albums. It also rejects hidden file
#       requests and paths starting with "/".
import os
import re

#Contains functions and variables used by both viewing and browsing.

#Template files are normal HTML, with the exception of one line which
#contains only "${content}" to indicate that the HTML generated should be placed
#there. It is expected that the template includes the relevant CSS.
#    All styling is done via CSS. To alter the HTML generated change the format
#    strings found in the album's code.

#Offline settings
document_root = "../../"
web_icons_dir = "../photo_albums/icons/"
server_photo_dir = "../photo_albums/photos/"
web_photo_dir = server_photo_dir
is_online = False
link_base = ''

    # Used to ensure that the entire image (in view) is visible onscreen
    #  It is an alternative to JavaScript resizing the image to be visible.
    #  TODO: Use JavaScript solution instead to provide a better experience.
    # Also used to ensure that  it scrolls down to show as many folders as
    #  possible (which is very useful on mobile devices).

    # Causes the browser to scroll down so that the albums navigation bar is at
    # the top of the screen, but only if it can scroll down (ie. when content would
    # be offscreen)
link_tail = '#albums-bar'

#Online settings
if os.path.exists("/srv/www/yorkbeach"):
    document_root = "/srv/www/yorkbeach/"
    server_photo_dir = document_root+"photo_albums/albums/"
    web_photo_dir = "/photo_albums/albums/"
    web_icons_dir = "/photo_albums/icons/"
    link_base = "/photo_albums/"
    is_online = True

#Both offline and online
query_path = os.environ["QUERY_STRING"] # May be edited by users of this module
any_error = "" # Contains error message to be displayed (if any)

# Templates used by all sections of albums
# Navigation bar, location bar is given by a HTML list, items can be generated
# using folder_list_item. Code for nav is specific to module
folder_list_item = """\
            <li><a href="{url}">{name}</a></li>
"""

#Places an error message in a suitable block
error_msg = """\
<div class="error_msg">{message}</div>
"""

def clean_path(tainted_path):
    """Searchs for accessing hidden files, moving up directories and attempting
    to access a home directoryr
    Returns True if the path does none of these things
    """
    return not bool(re.search(r"(__|^\.|/\.|\.\.|~|\\|\./|//|^/)", tainted_path))

real_document_root = os.path.realpath(document_root)
def is_safe_path(path):
    """Checks that the path is inside the server root.
        i.e. Doesn't contain a symlink accessing private server data
    """
    return os.path.realpath(path).startswith(real_document_root)

def is_image(filename):
    """Checks that the file extension is jpg, png or svg"""
    return (filename.endswith(".jpg") or filename.endswith(".JPG")
            or filename.endswith(".png") or filename.endswith(".svg"))

def print_header_only(template_filelines):
    """Prints up to ${content} in a file"""
    curr_line = 0
    while template_filelines[curr_line]!="${content}\n":
        print(template_filelines[curr_line],end='')
        curr_line += 1
    return curr_line+1

def split_images_folders(path):
    """Returns two separate alphabetical lists, of the folders and images in a directory
        The first is the images, second the folders, each as a list of their
        names.
        Fails if the path is unsafe.
    """
    assert(is_safe_path(path))
    all_files = os.listdir(path)
    all_files.sort() #Sorted as isn't by default
    images = []
    folders = []
    for filename in all_files:
        if filename[0]=='.': #Skip hidden files
            pass
        full_path = path+'/'+filename
        # No check for symlinks, as will fail if an unsafe folder is opened
        if os.path.isdir(full_path):
            folders.append(filename)
        elif os.path.isfile(full_path) and is_image(filename):
            images.append(filename)
    return (images,folders)
