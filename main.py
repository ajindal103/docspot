from urllib import response
import cv2
import tkinter as tk
from tkinter import filedialog
from tkinter import *
from tkinter.filedialog import askopenfile
from fileinput import filename
import os
import os.path
from pathlib import Path
import time
from datetime import datetime
import PIL.Image
from PIL import ImageTk
import PIL
from PIL import ImageDraw, ImageFont
import numpy as np
from PIL import Image
import glob
from pdf2docx import Converter
from pdf2image import convert_from_path
from PyPDF2 import PdfMerger
from urllib.request import urlopen
from skimage.filters import threshold_local
from flask import Flask, redirect, render_template

app = Flask(__name__)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/scan')
def scanner():
    root = Tk()
    root.configure(background='#11379F')
    root.title("Docspot Scanner")
    width = root.winfo_screenwidth()
    height = root.winfo_screenheight()
    root.geometry(f'{width}x{height}')

    root.resizable(0, 0)
    launch = False

    w = 385
    h = 535
    size = (w, h)

    def launchCamera():
        global capture_button, crop_count, crop_images, pdf_count, pdf_button, scanned_imgs
        url = url_text.get()
        crop_count = 0
        pdf_count = 0
        scanned_imgs = []

        capture_button = tk.Button(root, text='Capture Image', bg="white", fg="#11379F", width=22,
                                   height=1, font=('roboto', 20, ' bold '), command=crop_image, activebackground='green')
        capture_button.place(x=24, y=620)

        pdf_button = Button(root, borderwidth=0, command=pdf_gen, width=15,
                            text='Download PDF', bg='white', fg="#11379F", font=('roboto', 11, 'bold'))
        pdf_button.pack()
        pdf_button.place(x=900, y=35)

        try:
            if url == '':
                notify1 = tk.Label(root, text='Check The URL!!', width=20, height=1, fg="white", bg="red",
                                   font=('roboto', 13, ' bold '))
                notify1.place(x=24, y=68)
                root.after(2000, destroy_widget, notify1)
                capture_button.destroy()
                pdf_button.destroy()
            else:
                global display, img_frame, close_button, img
                img_frame = tk.Frame(root)
                img_frame.place(x=24, y=80)

                display = tk.Label(img_frame)
                display.grid()

                close_button = tk.Button(root, text='CLOSE', bg="white", fg="#11379F", width=12, borderwidth=0,
                                         height=0, font=('roboto', 11, 'bold '), command=destroy_cam,
                                         activebackground='red')
                close_button.place(x=400, y=35)

                def show_frame():
                    global img
                    img_resp = urlopen(url)
                    img_arr = np.array(
                        bytearray(img_resp.read()), dtype=np.uint8)
                    frame = cv2.imdecode(img_arr, -1)
                    frame = cv2.rotate(frame, cv2.cv2.ROTATE_90_CLOCKWISE)

                    cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
                    rgb = cv2.cvtColor(cv2image, cv2.COLOR_RGBA2RGB)
                    img = PIL.Image.fromarray(rgb)
                    img1 = img.resize(size, PIL.Image.ANTIALIAS)
                    imgtk = ImageTk.PhotoImage(image=img1)
                    display.imgtk = imgtk
                    display.configure(image=imgtk)
                    display.after(10, show_frame)

                show_frame()
        except Exception as e:
            print(e)
            notify2 = tk.Label(root, text='Connection Closed!', width=20, height=1, fg="white", bg="red",
                               font=('roboto', 13, ' bold '))
            notify2.place(x=24, y=68)
            root.after(2000, destroy_widget, notify2)
            img_frame.destroy()
            display.destroy()
            pdf_button.destroy()
            close_button.destroy()
            capture_button.destroy()

    def destroy_widget(widget):
        widget.destroy()

    def destroy_cam():
        img_frame.destroy()
        display.destroy()
        close_button.destroy()
        capture_button.destroy()

    def crop_image():
        global cropping, crop_count, launch, scanned_imgs
        launch = True

        repn = Path('Original_image')
        if repn.is_dir():
            pass
        else:
            os.mkdir('Original_image')
        crop_count += 1

        img1 = img.copy()
        img1 = cv2.cvtColor(np.asarray(img1), cv2.COLOR_RGB2BGR)
        cn = './Original_image/img_' + str(crop_count) + '.jpg'
        cv2.imwrite(cn, img1)

        orig_img_label = tk.Label(root, text="Orignal: " + cn[17:], width=23, height=1, fg="#11379F", bg="white",
                                  font=('roboto', 15, ' bold '))
        orig_img_label.place(x=430, y=140)

        orig_img_frame = tk.Frame(root)
        orig_img_frame.place(x=430, y=170)

        display2 = tk.Label(orig_img_frame)
        display2.grid()

        cv2image = cv2.cvtColor(img1, cv2.COLOR_BGR2RGBA)
        rgb = cv2.cvtColor(cv2image, cv2.COLOR_RGBA2RGB)
        img2 = PIL.Image.fromarray(rgb)
        img2 = img2.resize((270, 480), PIL.Image.ANTIALIAS)
        imgtk = ImageTk.PhotoImage(image=img2)
        display2.imgtk = imgtk
        display2.configure(image=imgtk)
        root.after(10000, destroy_widget, display2)
        root.after(10000, destroy_widget, orig_img_frame)
        root.after(10000, destroy_widget, orig_img_label)

        imgr = cv2.imread(cn)
        imgr = cv2.cvtColor(imgr, cv2.COLOR_BGR2GRAY)
        t = threshold_local(imgr, 35, offset=15, method='gaussian')
        imgr = (imgr > t).astype('uint8') * 255
        repn = Path('Scanned_image')
        if repn.is_dir():
            pass
        else:
            os.mkdir('Scanned_image')
        cn1 = './Scanned_image/img_' + str(crop_count) + '.jpg'
        cv2.imwrite(cn1, imgr)
        scanned_imgs.append(cn1)
        print(scanned_imgs)
        scanned_img_label = tk.Label(root, text="Scanned: " + cn[17:], width=23, height=1, fg="#11379F", bg="white",
                                     font=('roboto', 15, ' bold '))
        scanned_img_label.place(x=730, y=140)

        scan_img_frame = tk.Frame(root)
        scan_img_frame.place(x=730, y=170)

        display4 = tk.Label(scan_img_frame)
        display4.grid()

        cv2image4 = cv2.cvtColor(imgr, cv2.COLOR_GRAY2RGBA)
        rgb4 = cv2.cvtColor(cv2image4, cv2.COLOR_RGBA2RGB)
        img4 = PIL.Image.fromarray(rgb4)
        img4 = img4.resize((270, 480), PIL.Image.ANTIALIAS)
        imgtk4 = ImageTk.PhotoImage(image=img4)
        display4.imgtk = imgtk4
        display4.configure(image=imgtk4)
        root.after(10000, destroy_widget, display4)
        root.after(10000, destroy_widget, scan_img_frame)
        root.after(10000, destroy_widget, scanned_img_label)

    def pdf_gen():
        global pdf_count, pdf_button, launch, scanned_imgs
        print(launch)
        if launch == False:
            notify1 = tk.Label(root, text='Capture the Images first!', width=20, height=1, fg="white", bg="red",
                               font=('roboto', 13, ' bold '))
            notify1.place(x=24, y=68)
            root.after(2000, destroy_widget, notify1)
            destroy_cam()
            pdf_button.destroy()
        else:
            pdf_button.destroy()
            pdf_count += 1

            img = PIL.Image.new('RGB', (100, 30), color=(255, 255, 255))
            fnt = ImageFont.truetype('./meta/arial.ttf', 13)
            d = ImageDraw.Draw(img)
            d.text((5, 10), "DOCSPOT", font=fnt, fill=(0, 0, 0))
            img.save('./Scanned_image/index.jpg')
            scanned_imgs.append('./Scanned_image/index.jpg')

            image_list = []
            for image in scanned_imgs:
                img = PIL.Image.open(image)
                img = img.convert('RGB')
                image_list.append(img)
            image_list.pop(-1)
            path_new = filedialog.askdirectory(title="Select Save Location")
            ts = time.time()
            timeStam = datetime.fromtimestamp(ts).strftime('%H:%M:%S')
            Hour, Minute, Second = timeStam.split(":")
            save_here = os.path.join(path_new, str(pdf_count)+'_'+str(Hour)+'_' +
                                     str(Minute)+'_'+str(Second)+'.pdf')
            img.save(save_here, save_all=True, append_images=image_list)

            notify1 = tk.Label(root, text='PDF Generated!!', width=20, height=1, fg="white", bg="green",
                               font=('roboto', 13, ' bold '))
            notify1.place(x=24, y=68)
            root.after(2000, destroy_widget, notify1)
            destroy_cam()

    url_heading = tk.Label(root, text="Enter Your URL", width=18, height=1, fg="white", bg="#11379F",
                           font=('roboto', 16, 'bold'))
    url_heading.place(x=-15, y=5)

    url_text = tk.Entry(root, borderwidth=0, width=30, bg="white",
                        fg="#11379F", font=('roboto', 16, ' bold '), relief=GROOVE)
    url_text.place(x=24, y=35)
    url_text.insert(0, 'http://192.168.0.101:8080/shot.jpg')

    start_button = tk.Button(root, text='START', bg="white", fg="#11379F", width=12, borderwidth=0,
                             height=0, font=('roboto', 11, 'bold '), command=launchCamera, activebackground='green')
    start_button.place(x=400, y=35)
    root.lift()
    root.attributes('-topmost', True)
    root.after_idle(root.attributes, '-topmost', False)
    root.mainloop()
    return redirect('/')


@app.route('/jpg-pdf')
def jpgpdf():
    imaze_list = []

    imaze = filedialog.askopenfilenames(title="Select Images")
    imazes = list(imaze)
    for imz in imazes:
        im = PIL.Image.open(imz)
        im = im.convert('RGB')
        imaze_list.append(im)

    path_new = filedialog.askdirectory(title="Select Save Location")
    date = datetime.now().strftime('%Y%m%d%I%M%S')
    filename = f'Converted_{date}'
    save_here = os.path.join(path_new, filename+'.pdf')
    imaze_list[0].save(save_here, save_all=True, append_images=imaze_list[1:])
    return redirect('/')


@app.route('/pdf-word')
def pdfword():
    pdf = filedialog.askopenfilename(title="Select PDF File")

    path_new = filedialog.askdirectory(title="Select Save Location")
    date = datetime.now().strftime('%Y%m%d%I%M%S')
    filename = f'WordFile_{date}'
    save_here = os.path.join(path_new, filename+'.docx')

    cv = Converter(pdf)
    cv.convert(save_here, start=0, end=None)
    cv.close()
    return redirect('/')


@app.route('/pdf-jpg')
def pdfjpg():
    pdf = filedialog.askopenfilename(title="Select PDF File")
    pages = convert_from_path(pdf)

    path_new = filedialog.askdirectory(title="Select Save Location")

    for i in range(len(pages)):
        date = datetime.now().strftime('%Y%m%d%I%M%S')
        filename = "page"+str(i)+f'_{date}'
        save_here = os.path.join(path_new, filename+'.jpg')
        pages[i].save(save_here, "JPEG")
    return redirect('/')


@app.route('/pdf-merge')
def pdfmerge():
    pdf_list = filedialog.askopenfilenames(title="Select PDF Files")
    pdfs = list(pdf_list)
    merger = PdfMerger()
    for pdf in pdfs:
        merger.append(pdf)

    path_new = filedialog.askdirectory(title="Select Save Location")
    date = datetime.now().strftime('%Y%m%d%I%M%S')
    filename = f'Merged_{date}'
    save_here = os.path.join(path_new, filename+'.pdf')

    merger.write(save_here)
    merger.close()
    return redirect('/')


if __name__ == "__main__":
    app.run(debug=True)
