"""
Functions used for handling exchange credentials. Contains functions for 
encrypting/decrypting the credential file, as well as an exchange class for 
storing exchange information for use. \
"""

import time, os, sys, transpositionEncrypt, transpositionDecrypt

#TODO:
#GENERATE EXCHANGE CLASS
#HANDLE THE CREDENTIAL FILE



def encrypt(password, credfile = "credentials.txt"):
	"""Function for encrypting the credential file"""
	if not os.path.exists(credfile):
		print('The credential file %s does not exist. Quitting...' % (credfile))
		sys.exit()

	fileObj = open(credfile)
	content = fileObj.read()
	fileObj.close()

	#encrypt file
	encrypted = transpositionEncrypt.encryptedMessage(password, content)

	#output to file, save as filename_encrypted and delete the original file
	outputFileObj = open('credentials_encrypted.txt', 'w')
	outputFileObj.write(translated)
	outputFileObj.close()

	#remove the original file
	os.remove(credfile)


def decrypt(password, credfile = "credentials_encrypted.txt"):
	"""Function for decrypting credential file"""
	if not os.path.exists(credfile):
		print('The credential file %s does not exist. Quitting...' % (credfile))
		sys.exit()

	#open file
	fileObj = open(credfile)
	content = fileObj.read()
	fileObj.close()

	#decrypt file
	decrypted = transpositionEncrypt.decryptedMessage(password, content)

	#output to file
	outputFileObj = open('credentials.txt', 'w')
	outputFileObj.write(translated)
	outputFileObj.close()

	#handle credentials and create the exchange object
	###HANDLE FILE

	#remove the unencrypted file
	os.remove("credentials.txt")

	return Exchanges
