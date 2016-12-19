# view
Online image browser/viewer (photo albums), generated using CGI.

## Summary
Images are organised into folders. Folders within folders are supported.

The images are stored in a directory hierachy. Different directories are
different folders. Thumbnails can be provided in a parallel directory structure.
If thumbnails are not provided the full resolution images are used as
thumbnails.

A HTML template file is used to set the styling, any navigation bar, etc. around
the output.

The main CGI script is `view.py`. See "Queries".

## Requirements
- Python 3.
- A server supporting CGI.

## Settings
Found in `view_settings.py`.

For simplicity the settings are Python variables.  You do not need to know
Python to set them (see "Types" below).

A setting is of the form `[name] = [value]`. So just replace the part after the `=`.
### Filesystem paths
<dl>
<dt>document_root</dt> <dd>(String) Folder which files accessed are required to
be contained in, protects against symbolic links.
<dt>server_photo_dir</dt> <dd>(String) Location of images in filesystem.</dd>
<dt>server_thumbnails_dir</dt> <dd>(String) Location of thumbnails in filesystem
(if any).</dd>
<dt>template_file</dt> <dd>(String) HTML file to inject image view/folder
listings into for output.</dd>
</dl>
### Web root relative paths
<dl>
<dt>web_icons_dir</dt> <dd>(String) Icons (next, previous, folder, ...)
directory.</dd>
<dt>web_photo_dir</dt> <dd>(String) Images directory.</dd>
<dt>web_thumbnails_dir</dt> <dd>(String) Thumbnails directory (if any).</dd>
<dt>link_base</dt> <dd>(String) Prefix for any image/folder links. Typically set
to <code>"?"</code>. This setting is used for URL rewriting support.</dd>
</dl>
### Other
<dl>
<dt>output_mime</dt> <dd>(Boolean) Should the MIME type be output (should be
<code>True</code> when accessed via CGI).</dd>
</dl>

### Types
These are specified in () just before the description of the given setting.
<dl>
<dt>String</dt> <dd><code>"..."</code>. The <code>...</code> is the content in the string.</dd>
<dt>Boolean</dt> <dd>Either <code>True</code> or <code>False</code>.</dd>
</dl>

## Data Storage
In the `server_photo_dir` each directory contains all the images (JPG, SVG or
PNG) meant to be in the folder of with its name.

### Thumbnails
Stored in `server_thumbnails_dir`. This directory should have the same file tree
(directories and filenames) as `server_photo_dir`. The difference being that the
images stored are compressed versions of those in `server_photo_dir`.

If the directory for the thumbnails of images in a folder doesn't exist, the
full resolution images are used as thumbnails.

### Naming
The name of a folder/image is its name, dropping any extension and replacing all
'\_' with ' '. Any image extensions should be in lowercase.

### Ordering
Images and folders are sorted alphabetically (with folders first) by the real
name for both folder listings and determining the next/previous image.

## Template
This is a HTML file, which one line being just `${content}`. This line is where
the generated HTML for the folders is inserted.

An example is found in `example/`. This includes some JavaScript to create a
slideshow.

It should be noted that the styles and JavaScript are heavily dependent on the
current output format. It is unlikely to change, but any changes would break the
supplied example.

### Styling
By default the output is not styled. This is for maximum flexibility. The
template should include a style sheet to do so (otherwise the output isn't
pretty).
### JavaScript
No JavaScript is inserted automatically. The same caveats as for styling apply.

## Security
### Paths
Access to paths outside `document_root` is prohibited, this includes doing so
via a symbolic link. The script is permitted to abort and produce no output if
this happens.

The images directory and template file *must* exist.

If a path does not exist (and does not violate the above), then an appropriate
error message is displayed.

### XSS
All output depending on a query has any potentially dangerous characters escaped.

## Queries
The entire query (bit after the `?`) is the path to view (inside the images
directory).

Typically the user sends their queries to `view.py`. It is possible to pass the
query directly to `view_image.py` and `view_folder.py`; This may be removed in
the future.
