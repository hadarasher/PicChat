"""
Opens an image and look at the pixels in hexadecimal.
If the pixels blue channel falls in the 0-5 range then 1 bit of information is stored.
Ends the stream with a delimeter of fifteen 1's and a 0 to take up 2 bytes.
When time times to retrieve it pulls all the blue bits of 0 and 1 until the stream obtains
the delimeter of fifteen 1's and a 0.
https://www.youtube.com/watch?v=q3eOOMx5qoo
"""
from PIL import Image
import binascii


def str2bin(msg):
    #bin_msg = bin(int(binascii.hexlify(msg), 16))
    bin_msg=''
    for i in range(len(msg)):
        if not msg[i].isalnum():
            bin_msg=bin_msg+str(0)+str(bin(ord(msg[i])))[2:]
        else:
            bin_msg=bin_msg+str(bin(ord(msg[i])))[2:]
    return bin_msg

def bin2str(bin_msg):
    #msg = binascii.unhexlify('%' % (int('b' + bin_msg, 2)))
    #return ''.join(chr(int(bin_msg[i:i+8], 'b')) for i in xrange(0, len(bin_msg), 7))
    #return (bin_msg).decode('ascii')
    msg=''
    for i in range(0,len(bin_msg),7):
        #print "the ascii value: "+binascii.unhexlify('0'+bin_msg[i:i+7])
        msg=msg+chr(int('0'+bin_msg[i:i+7],2))
    return msg

def rgba2hex(r, g, b, a):
    return '#{:02x}{:02x}{:02x}{:02x}'.format(r, g, b, a)

def hex2rgba(hexcode):
    #return tuple(map(ord, hexcode[1:].decode('hex')))
    return int(str(hexcode[1:3]),16),int(str(hexcode[3:5]),16),int(str(hexcode[5:7]),16),int(str(hexcode[7:9]),16)

def encode(hexcode, digit):
    if hexcode[-1] in ['0', 'b', 'c', 'd', 'e', 'f']:
        hexcode = hexcode[:-1] + digit
        return hexcode
    else:
        return None

def decode(hexcode):
    if hexcode[-1] in ('0', '1'):
        return hexcode[-1]
    else:
        return None

def hide_msg(img_name, msg):
    new_img_name = 'new_' + img_name
    img = Image.open(img_name)
    bin_msg = str2bin(msg) + b'1111111111111110'

    if img.mode in ('RGBA'):  #could be rgb or rgba
        img = img.convert('RGBA')
        data = img.getdata()

        new_data = []
        digit = 0
        for item in data:
            if digit < len(bin_msg):
                new_pixel = encode(rgba2hex(item[0], item[1], item[2], item[3]), bin_msg[digit])
                if new_pixel == None:
                    new_data.append(item)
                else:
                    (r, g, b, a) = hex2rgba(new_pixel)
                    new_data.append((r, g, b, a))
                    digit += 1
            else:
                new_data.append(item)
        img.putdata(new_data)
        img.save(new_img_name, 'png')
        print 'done'
        return new_img_name
    return "incorrect image mode.."

def unhide_msg(img):
    img = Image.open(img)
    bin_msg = ''

    if img.mode != ('RGBA'):
        return "incorrect image mode."
    #img = img.convert('RGBA')
    data = img.getdata()

    for item in data:
        print "aaaaaaaaaaaaaaaaa"
        digit = decode(rgba2hex(item[0], item[1], item[2], item[3]))

        if digit is None:
            pass
        else:
            bin_msg = bin_msg + digit
            if bin_msg[:-16] == '1111111111111110':
                print "kkkkkkkkkkkkkk"
                return bin2str(bin_msg[:-16])
    return bin2str(bin_msg[:-16])

def encode_image(img, msg):
    """
    use the red portion of an image (r, g, b) tuple to
    hide the msg string characters as ASCII values
    red value of the first pixel is used for length of string
    """
    length = len(msg)
    # limit length of message to 255
    if length > 255:
        print("text too long! (don't exeed 255 characters)")
        return False
    if img.mode != 'RGB':
        print("image mode needs to be RGB")
        return False
    # use a copy of image to hide the text in
    encoded = img.copy()
    width, height = img.size
    index = 0
    for row in range(height):
        for col in range(width):
            r, g, b = img.getpixel((col, row))
            # first value is length of msg
            if row == 0 and col == 0 and index < length:
                asc = length
            elif index <= length:
                c = msg[index - 1]
                asc = ord(c)
            else:
                asc = r
            encoded.putpixel((col, row), (asc, g, b))
            index += 1
    return encoded

def decode_image(img):
    """
    check the red portion of an image (r, g, b) tuple for
    hidden message characters (ASCII values)
    """
    width, height = img.size
    msg = ""
    index = 0
    for row in range(height):
        for col in range(width):
            try:
                r, g, b = img.getpixel((col, row))
            except ValueError:
                # need to add transparency a for some .png files
                r, g, b, a = img.getpixel((col, row))
            # first pixel r value is length of message
            if row == 0 and col == 0:
                length = r
            elif index <= length:
                msg += chr(r)
            index += 1
    return msg

def get_img_data(img):
    with open(img,"rb") as f:
        image=f.read()
        return image

def make_img_file(data):
    print "trying to make new"
    with open("stgg.png","wb") as f:
        f.write(data)
    return "stgg.png"

def main():
    msg = "this is a secret massage!"
    img = "stg.png"
    new_img = hide_msg(img, msg)
    print unhide_msg(new_img)
    print get_img_data("stg.png")

if __name__=="__main__":
    main()


"""
img = "stg.png"

imgOpen = Image.open(img)
##print hex2rgb(rgb2hex(img.getpixel(0, 0, 0)))
# image mode needs to be 'RGB'
print(img, imgOpen.mode)  # test
# create a new filename for the modified/encoded image
encoded_image_file = "enc_" + img
# don't exceed 255 characters in the message
secret_msg = "this is a secret message added to the image"
print(len(secret_msg))  # test
img_encoded = encode_image(imgOpen, secret_msg)
if img_encoded:
    # save the image with the hidden text
    img_encoded.save(encoded_image_file)
    print("{} saved!".format(encoded_image_file))

    # get the hidden text back ...
    img2 = Image.open(encoded_image_file)
    hidden_text = decode_image(img2)
    print("Hidden text:\n{}".format(hidden_text))
"""

