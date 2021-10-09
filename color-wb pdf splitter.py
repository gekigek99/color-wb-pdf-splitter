# version 1.0.0

# fitz error:
#   pip uninstall fitz
#   pip install pymupdf

from time import time
from os import system
from sys import exit
from PIL import Image
from PyPDF2 import PdfFileWriter, PdfFileReader
import io
import fitz

def main():
    inputfile = input('insert pdf to analyze: ')
    try:
        doc = fitz.open(inputfile)
    except:
        print('error opening file!')
        system("PAUSE")
        exit()
    doc_lenght = len(doc)
    print("file: %s, pages: %s, objects: %s" % (inputfile, doc_lenght, countPdfImg(doc)))

    pages_containing_images = []
    rgb_pages = []
    rgb_pages_printable = []
    wb_pages_printable = []

    t0 = time()
    
    pages_containing_images, rgb_pages = extract_images_rgb(doc)

    rgb_pages_printable = convert_to_printable_pages(rgb_pages, doc_lenght)
    wb_pages_printable = get_wb_pages_printable(doc_lenght, rgb_pages_printable)

    makepdf(inputfile, rgb_pages_printable, 'rgb')
    makepdf(inputfile, wb_pages_printable, 'wb')

    pages_containing_images = pageshifter(pages_containing_images, 1)
    rgb_pages = pageshifter(rgb_pages, 1)
    rgb_pages_printable = pageshifter(rgb_pages_printable, 1)
    wb_pages_printable = pageshifter(wb_pages_printable, 1)
    
    t1 = time()
    print("run time:", round(t1-t0, 2), 's')
    print('pages that contain images:\n', pages_containing_images)
    print('pages that contain RGB images:\n', rgb_pages)
    print('rgb pages to print (', len(rgb_pages_printable), '):\n', rgb_pages_printable)
    print('wb pages to print (', len(wb_pages_printable), '):\n', wb_pages_printable)
    print('press enter to do an other document...')
    system("PAUSE")

def countPdfImg(doc):
    tot = 0

    # iterate over PDF pages
    for page_index in range(len(doc)):
        # get the page itself
        page = doc[page_index]
        image_list = page.getImageList()

        tot += len(image_list)
    
    return tot

def extract_images_rgb(doc):
    pages_containing_images = []
    rgb_pages = []

    for page_index in range(len(doc)):
        print(' ' * 10, end = '\r')
        print(round(100 * page_index / len(doc)), '%', end = '')

        # get the page itself
        page = doc[page_index]
        image_list = page.getImageList()
        if len(image_list) != 0:
            pages_containing_images.append(page_index)
        
        for image_index, img in enumerate(image_list, start=1):
            # get the XREF of the image
            xref = img[0]
            # extract the image bytes
            base_image = doc.extractImage(xref)
            image_bytes = base_image["image"]
            # get the image extension
            image_ext = base_image["ext"]
            # load it to PIL
            image = Image.open(io.BytesIO(image_bytes))
            
            if page_index not in rgb_pages:
                if RGBimageanalyze(image) == True:
                    rgb_pages.append(page_index)
    
    print(' ' * 10, end = '\r')
    print('100 %')
    return pages_containing_images, rgb_pages

def convert_to_printable_pages(rgb_pages, doc_lenght):
    rgb_pages_printable = []
    for i in range(len(rgb_pages)):
        if rgb_pages[i] % 2 == 0:           #even (page 0,2,4...)
            if rgb_pages[i] not in rgb_pages_printable:
                rgb_pages_printable.append(rgb_pages[i])
            if rgb_pages[i] + 1 not in rgb_pages_printable and rgb_pages[i] +1 < doc_lenght:
                rgb_pages_printable.append(rgb_pages[i] + 1)
        else:                               #odd (page 1,3,5...)
            if rgb_pages[i] - 1 not in rgb_pages_printable:
                rgb_pages_printable.append(rgb_pages[i] - 1)
            if rgb_pages[i] not in rgb_pages_printable:
                rgb_pages_printable.append(rgb_pages[i])
    return rgb_pages_printable

def get_wb_pages_printable(doc_lenght, rgb_pages_printable):
    wb_pages_printable = []
    for i in range(doc_lenght):
        if i not in rgb_pages_printable:
            wb_pages_printable.append(i)
    return wb_pages_printable

def makepdf(inputfile, pages_printable, color):                
    inpdf = PdfFileReader(inputfile, strict=False)
    outpdf = PdfFileWriter()

    for i in range(len(pages_printable)):
       outpdf.addPage(inpdf.getPage(pages_printable[i]))

    if color == 'rgb':
        with open(inputfile.replace('.pdf', ' ') + '(for color pages printing).pdf', "wb") as out_file:
            outpdf.write(out_file)
            print('written file: rgb_pages_to_print.pdf')
    if color == 'wb':
        with open(inputfile.replace('.pdf', ' ') + '(for wb pages printing).pdf', "wb") as out_file:
            outpdf.write(out_file)
            print('written file: wb_pages_to_print.pdf')

#-------------------------------TOOLS-------------------------------#

def RGBimageanalyze(im):
    if im.mode != "RGB" and im.mode != "RGBA":
        im = im.convert("RGB")
    pix = im.load()
    for y in range(0, im.size[1], precision):
        for x in range(0, im.size[0], precision):
            r = pix[x,y][0]
            b = pix[x,y][1]
            g = pix[x,y][2]
            avg = (r + b + g) / 3
            if avg - grey_approx_coeff <= r <= avg + grey_approx_coeff and avg - grey_approx_coeff <= b <= avg + grey_approx_coeff and avg - grey_approx_coeff <= g <= avg + grey_approx_coeff:
                continue
            else:
                im.close()
                return True
    im.close()
    return False

def pageshifter(input_list, shift):
    output_list = []
    for i in range(len(input_list)):
        output_list.append(input_list[i] + shift)
    return output_list
    
    
if __name__ == '__main__':
    grey_approx_coeff = input('grey_approx_coeff (between 0 and 50 (0 --> must be perfect gray (eg. rgb = 154,154,154))) [default = 5]: ')    #between 0 and 50 (0 --> must be perfect gray (eg. rgb = 154,154,154))
    precision = input('precision (between 1 and 10 (1 --> more precise (takes more time))) [default = 5]: ')                                  #between 1 and 10 (1 --> more precise (takes more time))
    if not grey_approx_coeff.isdigit():
        grey_approx_coeff = 5
    if not precision.isdigit():
        precision = 5
    grey_approx_coeff = int(grey_approx_coeff)
    precision = int(precision)
    while True:
        main()
