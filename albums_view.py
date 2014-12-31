#!/usr/bin/python3

# Copyright Matthew Pottage 2014
# Produces photo albums for a website, based on the directory hierachy of a
# specified directory.
# Security Assumptions: Attacker has direct or indirect access to script via http/https,
#   can edit files inside document_root (excluding the albums code) via sftp.

import os
import albums_common as common

#Displays a single image on a page.
# Configuration is in common.
# The template is set here, details on templates are found in albums_common.py.

#Offline extra settings
view_template_file = "../photo_albums/view-template.html"
#Online extra settings
if common.is_online:
    view_template_file = common.document_root+"/photo_albums/view-template.html"

navigation = """\
<header id="albums-bar">
    <nav id="location">
        <ol>
        {folders_list}
        </ol>
    </nav>
    <div id="next-previous">
        <a href="{previous_link}" id="previous-image"><span>Previous</span></a><!--
        --><a href="{next_link}" id="next-image"><span>Next</span></a>
    </div>
</header>
"""

image = """\
<figure class="large-image">
    <img src="{img_url}" alt="{caption}">
    <figcaption>{caption}</figcaption>
</figure>
"""

nav_curr_image = """\
            <li><span id="current-file" class="image-name">{name}</span></li>
"""

class Image:
    """Represents an image. Collects together all the values used to display
    one."""
    def __init__(self, r_albums_addr):
        """Assumes that r_albums_addr refers to an image"""
        path_parts = r_albums_addr.rsplit('/', 1)
        self.directory = path_parts[0]
        self.name      = path_parts[1].rsplit('.')[0].replace('_',' ')
        self.caption   = self.name
        self.raw_url   = common.web_photo_dir+r_albums_addr

        #Finding next and previous images
        images_in_dir  = common.split_images_folders(
                common.server_photo_dir+self.directory)[0]
        index = images_in_dir.index(path_parts[1])
        link_next_base = common.link_base+self.directory+'/'
        if index+1 >= len(images_in_dir):
            self.next_image = link_next_base+images_in_dir[0]
        else:
            self.next_image = link_next_base+images_in_dir[index+1]
        self.previous_image = link_next_base+images_in_dir[index-1]

def gen_nav_html(img):
    """Generates a list containing the current directory and all those above it
    for navigation. Also creates a link to the next image and the previous one.
    """
    path_parts = img.directory.split('/')
    nav_items = ""
    nav_items += common.folder_list_item.format(
            url=common.link_base+common.link_tail, name="All")
    for index,name in enumerate(path_parts):
        url = common.link_base+'/'.join(path_parts[:index+1])+'/'+common.link_tail
        nav_items += common.folder_list_item.format(
                url=url, name=name.replace('_', ' ')
                )

    nav_items += nav_curr_image.format(name=img.name)

    return navigation.format(folders_list=nav_items,
            next_link=img.next_image+common.link_tail,
            previous_link=img.previous_image+common.link_tail)
def gen_image_html(img):
    """Creates the <figure> containing the displayed image"""
    return image.format(img_url=img.raw_url, caption=img.caption)

def print_page():
    if common.is_online:
        print("Content-Type: text/html\n")

    assert(common.is_safe_path(view_template_file))
    template_file = open(view_template_file).readlines()
    template_file_line = common.print_header_only(template_file)

    # Image can't be instantiated if there is an error
    if common.any_error:
        print(common.any_error,end='')
    else:
        img = Image(common.query_path)
        print(gen_nav_html(img))
        print(gen_image_html(img))

    while template_file_line < len(template_file): #Print rest of template
        print(template_file[template_file_line],end='')
        template_file_line += 1



def main():
    """Starts HTML generation and validates paths used"""

    # CRITICAL error checking
    # Checks for files and folders that HAVE to exist
    assert(os.path.exists(common.server_photo_dir) and
            os.path.exists(view_template_file) and
            common.is_safe_path(common.server_photo_dir+'/'+common.query_path))
    # Path safety is normally checked at point of use, fails if unsafe
    # EXCEPTION: The viewed image address.

    # Recoverable error checking
    if (not common.clean_path(common.query_path) or
            not os.path.exists(common.server_photo_dir+common.query_path) or
            not common.is_image(common.query_path) ):
        common.any_error += common.error_msg.format(
                message="Sorry, the image \""+common.query_path+"\" does "
                "not exist.\n")
        common.query_path = "" # Default is to print no image

    print_page() # All errors safely handled, so now safe to print image.

if __name__=="__main__":
    main()