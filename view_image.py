#!/usr/bin/python3

# Copyright Matthew Pottage 2014
# See view_common.py.
import os
import html
import view_common as common

#Displays a single image on a page.

navigation_links = """\
    <div class="controls">
        <a href="{previous_link}" class="previous"><span>Previous</span></a><!--
        --><a href="{next_link}" class="next"><span>Next</span></a>
    </div>
"""

image = """\
<figure class="large-image">
    <img src="{img_url}" alt="">
    <figcaption>{caption}</figcaption>
</figure>
"""

nav_curr_image = """\
            <li><span class="current image-name">{name}</span></li>
"""

class Image:
    """Represents an image. Collects together all the values used to display
    one."""
    def __init__(self, r_image_addr):
        """Assumes that r_image_addr refers to an image"""
        path_parts = r_image_addr.rsplit('/', 1)
        raw_name = ''
        # If the image is in a subfolder
        if len(path_parts)==2:
            self.directory, raw_name = path_parts
        # If the image is in the photos dir (no subfolder)
        else:
            self.directory = ''
            raw_name = path_parts[0]
        self.name      = raw_name.rsplit('.')[0].replace('_',' ')
        self.caption   = self.name
        self.raw_url   = common.web_photo_dir+r_image_addr

        #Finding next and previous images
        #(both are this image if it is the only one in the folder).
        images_in_dir  = common.split_images_folders(
                common.server_photo_dir+self.directory)[0]
        index = images_in_dir.index(raw_name)
        link_next_base = common.link_base+self.directory+'/'
        if index+1 >= len(images_in_dir):
            self.next_image = link_next_base+images_in_dir[0]
        else:
            self.next_image = link_next_base+images_in_dir[index+1]
        self.previous_image = link_next_base+images_in_dir[index-1]

def gen_nav_html(img):
    """Generates the navigation for the albums.
    This includes a list containing the current directory and all those above it
    for the navigation bar and links to both the next image and the previous
    one.
    """
    nav_items = ""
    nav_items += common.location_list_item.format(
            url=common.link_base, name="All")
    if img:
        # No errors.
        path_parts = img.directory.split('/')
        for index,name in enumerate(path_parts):
            url = common.link_base+'/'.join(path_parts[:index+1])+'/'
            nav_items += common.location_list_item.format(
                    url=url, name=name.replace('_', ' ')
                    )

        nav_items += nav_curr_image.format(name=img.name)

        return common.header.format(header_content=common.location_list.format(ls=nav_items)+
                navigation_links.format(next_link=img.next_image,
                previous_link=img.previous_image))
    else:
        # A user input error, just show one link.
        return common.header.format(header_content=common.location_list.format(ls=nav_items))
def gen_image_html(img):
    """Creates the <figure> containing the displayed image"""
    return image.format(img_url=img.raw_url, caption=img.caption)

def print_page(query_path, error_html=""):
    if common.output_mime:
        print("Content-Type: text/html\n")

    assert(common.is_safe_path(common.template_file))
    template_file = open(common.template_file).readlines()
    template_file_line = common.print_header_only(template_file)

    # Image can't be instantiated if there is an error
    if len(error_html)>0:
        print(gen_nav_html(None))
        print(error_html,end='')
    else:
        img = Image(query_path)
        print(gen_nav_html(img))
        print(gen_image_html(img))

    common.print_rest(template_file, template_file_line)

def main():
    """Runs HTML generation and validates paths used to access and display the
    images.
    """
    query_path = common.raw_query_path()
    error_html = ""
    # CRITICAL error checking
    common.verify_core_paths();
    assert(common.is_safe_path(common.server_photo_dir+'/'+query_path))
    # Path safety is normally checked at point of use, fails if unsafe
    # EXCEPTION: The viewed image address.

    # Recoverable error checking
    if (not common.clean_path(query_path) or
            not os.path.exists(common.server_photo_dir+query_path) or
            not common.is_image(query_path) ):
        error_html += common.error_msg.format(
                message="Sorry, the photo <q>"+html.escape(query_path)+"</q> does "
                "not exist.\n")
        query_path = "" # Default is to print no image

    print_page(query_path, error_html) # All errors now safely handled.

if __name__=="__main__":
    main()
