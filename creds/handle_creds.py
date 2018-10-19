"""
Functions used for handling exchange credentials. Contains functions for 
encrypting/decrypting the credential file, as well as an exchange class for 
storing exchange information for use. \
"""

import time, os, sys, transpositionEncrypt, transpositionDecrypt


## class Exchange():


def encrypt(password):
	"""Function for encrypting the credential file"""
	filename = 'credentials.txt'
	if not os.path.exists(filename):
		print('The credential file %s does not exist. Quitting...' % (filename))
		sys.exit()

	fileObj = open(filename)
	content = fileObj.read()
	fileObj.close()

	#encrypt file
	encrypted = transpositionEncrypt.encryptedMessage(password, content)

	#output to file, save as filename_encrypted and delete the original file
	outputFileObj = open('credentials_encrypted.txt', 'w')
	outputFileObj.write(translated)
	outputFileObj.close()

	#remove the original file
	os.remove(filename)


def decrypt(password, passwordfile):
	"""Function for decrypting credential file"""
	if not os.path.exists(passwordfile[:-4] +'_encrypted.txt'):
		print('The credential file %s does not exist. Quitting...' % (passwordfile[:-4] +'_encrypted.txt'))
		sys.exit()

	#open file
	fileObj = open(passwordfile[:-4] +'_encrypted.txt')
	content = fileObj.read()
	fileObj.close()

	#decrypt file
	decrypted = transpositionEncrypt.decryptedMessage(password, content)

	#output to file
	outputFileObj = open('credentials.txt', 'w')
	outputFileObj.write(translated)
	outputFileObj.close()

	#handle credentials and create the exchange object

	#remove the original file
	os.remove(credentials_encrypted)
