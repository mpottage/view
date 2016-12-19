#!/usr/bin/python3

# Copyright Matthew Pottage 2015
# See view_common.py.
import os
import html
import view_common as common

# Configuration is done using the variables in view_common.py.

image_thumbnail = """\
    <figure>
        <a href="{view_url}" class="button">
            <div class="thumbnail-only">
                <img src="{img_url}" alt="">
            </div>
            <div class="name">{name}</div>
        </a>
    </figure>
"""
folder_thumbnail = """\
    <figure class="folder">
        <a href="{view_url}" class="button">
            <div class="thumbnail-only">
                <img src='"""+common.web_icons_dir+"""folder-white.svg' alt="">
            </div>
            <div class="name">{name}</div>
        </a>
    </figure>
"""
thumbnails_before = '<figure class="view thumbnails">\n'
thumbnails_after  = '</figure>\n'

def gen_thumbnails_html(query_path):
    """Generates the html to display all the thumbnails for images in the folder
    referenced by "query_path", assumes that split_images_folders checks for
    path safety.
    """
    res = thumbnails_before #Begin thumbnails container
    items = common.split_images_folders(common.server_photo_dir+query_path)
    # Nothing to display
    if not items[0] and not items[1]:
        res += "Empty"
    core_view_url = common.link_base+query_path
    core_photo_url = ""
    #Only show thumbnails if the directory for them is safe and exists,
    # as then presumably the thumbnails also exist.
    svr_thumbnails = common.server_thumbnails_dir+query_path
    if common.is_safe_path(svr_thumbnails) and os.path.exists(svr_thumbnails):
        core_photo_url = common.web_thumbnails_dir+query_path
    else:
        core_photo_url = common.web_photo_dir+query_path
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

def gen_nav_html(query_path):
    """Similar to gen_thumbnails_html, but for navigation"""
    path_parts = query_path.split('/')[:-1] #Assumed to end with '/'
    nav_folder_list = ""
    nav_folder_list += common.location_list_item.format(
            url=common.link_base, name="All")
    for index,name in enumerate(path_parts):
        url = common.link_base+'/'.join(path_parts[:index+1])+'/'
        nav_folder_list += common.location_list_item.format(
                url=url, name=name.replace('_', ' ')
                )
        
    return common.header.format(
            header_content=common.location_list.format(ls=nav_folder_list))

def print_page(query_path, error_html=""):
    if query_path and query_path[-1]!='/':
        query_path += '/'

    if common.output_mime:
        print("Content-Type: text/html\n")

    assert(common.is_safe_path(common.template_file))
    template_file = open(common.template_file).readlines()
    template_file_line = common.print_header_only(template_file)

    print(gen_nav_html(query_path))
    print(error_html,end='') #Does nothing if there is no message
    print(gen_thumbnails_html(query_path))

    common.print_rest(template_file, template_file_line)

def main():
    """Starts HTML generation and validates file paths used"""

    common.verify_core_paths()

    query_path = common.raw_query_path()
    error_html = ""
    # Recoverable error checking
    if (not common.clean_path(query_path) or
            not os.path.exists(common.server_photo_dir+query_path) ):
        error_html += common.error_msg.format(
                message="Sorry, the folder <q>"+html.escape(query_path)+""
                "</q> does not exist.\n")
        query_path = "" # Default is to print main directory

    print_page(query_path, error_html) # All errors safely handled.

if __name__=="__main__":
    main()
