#!/usr/bin/python3

# Copyright Matthew Pottage 2014
# Produces photo albums for a website, based on the directory hierachy of a
# specified directory.
# Security Assumptions: Attacker has direct or indirect access to script via http/https,
#   can edit files inside document_root (excluding the albums code) via sftp.
import os
import albums_common as common

#All links to files start with '/', indicating root of albums.
# ../, ~, ./, etc. are not permitted in links, even where valid.
# Configuration is done using the variables in albums_common.py.
# The template is set here, details on templates are found in albums_common.py.


#Offline extra settings (specific to browse)
browse_template_file = "../photo_albums/browse-template.html"
#Online extra settings
if common.is_online:
    browse_template_file = common.document_root+"/photo_albums/browse-template.html"

image_thumbnail = """\
    <figure>
        <a href="{view_url}" class="button">
            <div class="thumbnail-only">
                <img src="{img_url}" alt="{name}">
            </div>
            <div class="name">{name}</div>
        </a>
    </figure>
"""
folder_thumbnail = """\
    <figure class="folder-thumbnail">
        <a href="{view_url}" class="button">
            <div class="thumbnail-only">
                <img src='"""+common.web_icons_dir+"""folder-white.svg' alt="">
            </div>
            <div class="name">{name}</div>
        </a>
    </figure>
"""
navigation = """\
<header id="albums-bar">
    <nav id="location">
        <ol>
        {folders_list}
        </ol>
    </nav>
    <!--<div id="slideshow">
        <a href="{slideshow_link}">Slideshow</a>
    </div>-->
</header>
"""
thumbnails_before = '<figure class="albums-thumbnails">\n'
thumbnails_after  = '</figure>\n'

def gen_thumbnails_html():
    """Generates the html to display all the thumbnails for images in the folder
    referenced by "query_path", assumes that split_images_folders checks for
    path safety.
    """
    res = thumbnails_before #Begin thumbnails container
    items = common.split_images_folders(common.server_photo_dir+common.query_path)
    # Nothing to display
    if not items[0] and not items[1]:
        res += "Empty"
    core_view_url = common.link_base+common.query_path
    core_photo_url = common.web_photo_dir+common.query_path
    # Display folders first
    for folder in items[1]:
        name = folder.replace("_", " ")
        view_url = core_view_url+folder+'/'
        res += folder_thumbnail.format(name=name, view_url=view_url)
    for img in items[0]:
        name = img.rsplit(".",1)[0].replace("_", " ")
        img_url = core_photo_url+img
        view_url = core_view_url+img
        res += image_thumbnail.format(name=name,img_url=img_url,
            view_url=view_url)
    res += thumbnails_after #End thumbnails container
    return res

def gen_nav_html():
    """Similar to gen_thumbnails_html, but for navigation"""
    path_parts = common.query_path.split('/')[:-1] #Assumed to end with '/'
    nav_folder_list = ""
    nav_folder_list += common.folder_list_item.format(
            url=common.link_base, name="All")
    for index,name in enumerate(path_parts):
        url = common.link_base+'/'.join(path_parts[:index+1])+'/'
        nav_folder_list += common.folder_list_item.format(
                url=url, name=name.replace('_', ' ')
                )
        
    return navigation.format(folders_list=nav_folder_list, slideshow_link="#")

def print_page():
    if common.is_online:
        print("Content-Type: text/html\n")

    assert(common.is_safe_path(browse_template_file))
    template_file = open(browse_template_file).readlines()
    template_file_line = common.print_header_only(template_file)

    print(gen_nav_html())
    print(common.any_error,end='') #Does nothing if there is no message
    print(gen_thumbnails_html())

    while template_file_line < len(template_file): #Print rest of template
        print(template_file[template_file_line],end='')
        template_file_line += 1

def main():
    """Starts HTML generation and validates paths used"""
    #global common.query_path, common.any_error

    # CRITICAL error checking
    # Checks for files and folders that HAVE to exist
    assert(os.path.exists(common.server_photo_dir) and
            os.path.exists(browse_template_file))
    # Path safety is checked at point of use, fails if unsafe

    # Recoverable error checking
    if (not common.clean_path(common.query_path) or
            not os.path.exists(common.server_photo_dir+common.query_path) ):
        common.any_error += common.error_msg.format(
                message="Sorry, the album \""+common.query_path+"\" does not exist.\n")
        common.query_path = "" # Default is to print main directory
    elif common.query_path and common.query_path[-1]!='/':
        common.query_path += '/'

    print_page() # All errors safely handled, so now safe to handle query_string

if __name__=="__main__":
    main()
