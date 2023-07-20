# Importing library
import qrcode
 
# Data to be encoded
Class_Qrcode = "Put the iP address of your web server"
 
# Encoding data using make() function
img = qrcode.make(Class_Qrcode)
 
# Saving as an image file
img.save('SignUp.png')