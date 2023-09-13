import pygame
import mysql.connector
import cv2
import numpy as np
from time import sleep
from PIL import Image
import requests
import sys
import os
import time


def face_detect(chat_id):

    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read('trainer.yml')
    cascadePath = "data/haarcascade_frontalface_default.xml"
    faceCascade = cv2.CascadeClassifier(cascadePath);

    font = cv2.FONT_HERSHEY_SIMPLEX

    #iniciate id counter 
    id = 0
    c=0
    c1=0
    # names related to ids
    names = ['None'] 
    for i in range(1,101):
        names.append('user'+str(i))
    def tele_bot(chat_id):
        
        bot_token = '6449841998:AAHtJPCwWL55TzxtHnr1SJIzwg5BMnQHXQA'

        send_photo_url = f'https://api.telegram.org/bot{bot_token}/sendPhoto'

        image_path = 'stranger/user.jpg'  

        params = {
            'chat_id': chat_id,
        }

        with open(image_path, 'rb') as image_file:
            response = requests.post(send_photo_url, params=params, files={'photo': image_file})

        if response.status_code == 200:
            print('Image sent successfully!')
        else:
            print('Image sending failed.')
            print(response.text)


    
    cam = cv2.VideoCapture(0)


    i=0
    count=1

    while True:
        ret, img =cam.read()
        #img = cv2.flip(img, -1) # Flip vertically
        gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        
        faces = faceCascade.detectMultiScale( 
            gray,
            scaleFactor = 1.2,
            minNeighbors = 5
        )

        for(x,y,w,h) in faces:
            cv2.rectangle(img, (x,y), (x+w,y+h), (0,255,0), 2)
            id, confidence = recognizer.predict(gray[y:y+h,x:x+w])


            # Checking if confidence is less them 100 ==> "0" is perfect match 
            if (confidence < 70):
                id = names[id]
                
                confidence = "  {0}%".format(round(100 - confidence))
                if(count == 1):
                            print('face id:',str(id),' detected')
                            c-=1
                            count =0
                            i=0
                                        
            else:
                id = "unknown"
                print('no face detected')
                c+=1
                c1+=1
                if c==c1 and c==12:
                    
                    cv2.imwrite("stranger/user"+".jpg", gray[y:y+h,x:x+w])
                    tele_bot(chat_id)
                elif c!=c1:
                    
                    c=0
                    c1=0
                    
                    

                confidence = "  {0}%".format(round(100 - confidence))
                time.sleep(0.1)
                
            cv2.putText(img, str(id), (x+5,y-5), font, 1, (255,255,255), 2)
            cv2.putText(img, str(confidence), (x+5,y+h-5), font, 1, (255,255,0), 1)  
        
        cv2.imshow('camera',img)
        i= i+1
        if(i == 100):
            count=1
            i=0

        k = cv2.waitKey(10) & 0xff # Press 'ESC' for exiting video
        if k == 27:
            break

    #cleanup
    print("\n [INFO] Exiting Program and cleanup stuff")
    cam.release()
    cv2.destroyAllWindows()


def training():

    # Path for face image database
    path = 'dataSet'

    recognizer = cv2.face_LBPHFaceRecognizer.create() #cv2.face.createLBPHFaceRecognizer()
    detector = cv2.CascadeClassifier("data/haarcascade_frontalface_default.xml");

    # function to get the images and label data
    def getImagesAndLabels(path):
        imagePaths = [os.path.join(path,f) for f in os.listdir(path)]     
        faceSamples=[]
        ids = []
        for imagePath in imagePaths:
            PIL_img = Image.open(imagePath).convert('L') # converting it to grayscale
            img_numpy = np.array(PIL_img,'uint8')
            id = int(os.path.split(imagePath)[-1].split(".")[1])
            faces = detector.detectMultiScale(img_numpy)
            for (x,y,w,h) in faces:
                faceSamples.append(img_numpy[y:y+h,x:x+w])
                ids.append(id)
        return faceSamples,ids

    print ("\n [INFO] Training faces. It will take a few seconds. Wait ...")
    faces,ids = getImagesAndLabels(path)
    recognizer.train(faces, np.array(ids))

    # Saving the model into trainer/trainer.yml
    recognizer.save('trainer.yml') 

    # Printing the number of faces trained and end program
    print("\n [INFO] {0} faces trained. Exiting Program".format(len(np.unique(ids))))
    return


def face_dataset():

    cam = cv2.VideoCapture(0)
    cam.set(3, 640) 
    cam.set(4, 480)

    face_detector = cv2.CascadeClassifier('data/haarcascade_frontalface_default.xml')
    
    fp='dataset'
    files = os.listdir(fp)
    if os.listdir("dataset"):
        file_names = [int(str(f[5:7]) )for f in files if os.path.isfile(os.path.join(fp, f))]
        print(file_names)
        face_id=f'{max(file_names)+1:02}'
    else:
        face_id='01'

    print("\n [INFO] Initializing face capture. Look the camera and wait ...")

    # Initialize individual sampling face count
    count = 0

    while(True):
        ret, img = cam.read()
        #img = cv2.flip(img, -1) # flipping video image vertically
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_detector.detectMultiScale(gray, 1.3, 5)

        for (x,y,w,h) in faces:
            cv2.rectangle(img, (x,y), (x+w,y+h), (255,0,0), 2)     
            count += 1

            # Save the captured image into the datasets folder
            cv2.imwrite("dataset/User"+"." + face_id + '.' + str(count) + ".jpg", gray[y:y+h,x:x+w])

        cv2.imshow('image', img)

    # Press 'ESC' for exiting video
        if cv2.waitKey(100) & 0xff == ord('q'):
            break
        elif count >= 25: # Take 25 face sample and stop video
            break

    print("\n [INFO] Exiting Program and cleanup stuff")
    cam.release()
    cv2.destroyAllWindows()

#login Page

def login_interface(width, height):
    pygame.init()
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Login")

    # Font
    font = pygame.font.Font("Aldrich-Regular.ttf", 30)

    # Input box properties
    input_box1 = pygame.Rect(300, 200, 200, 50)
    input_box2 = pygame.Rect(300, 300, 200, 50)
    color_inactive = pygame.Color('lightskyblue3')
    color_active = pygame.Color('dodgerblue2')
    color = color_inactive
    active = False
    text1 = ''
    text2 = ''

    # MySQL database connection
    db = mysql.connector.connect(
        host="visionguarddb.cynkpxf20wc5.ap-south-1.rds.amazonaws.com",
        user="admin",
        password="9848Mysql",
        database="VisionGuardDB"
    )

    cursor = db.cursor()
    # Login button properties
    login_button = pygame.Rect(350, 400, 100, 50)

    running = True

    f=False

            




    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_box1.collidepoint(event.pos):
                    active = not active
                elif input_box2.collidepoint(event.pos):
                    active = not active
                elif login_button.collidepoint(event.pos):
                    # Check username and password against the database
                    cursor.execute("SELECT chat_id FROM users WHERE username=%s AND password=%s", (text1, text2))
                    result = cursor.fetchone()
                    if result:
                        chat_id = result[0]
                        print("Login successful! Chat ID:", chat_id)
                        db.close()
                        return chat_id
                    else:
                        print("Login failed. Please try again.")
                        f=True

                        

            if event.type == pygame.KEYDOWN:
                if active:
                    if event.key == pygame.K_RETURN:
                        # Check username and password against the database
                        cursor.execute("SELECT chat_id FROM users WHERE username=%s AND password=%s", (text1, text2))
                        result = cursor.fetchone()
                        if result:
                            chat_id = result[0]
                            print("Login successful! Chat ID:", chat_id)
                            db.close()
                            return chat_id
                        else:
                            print("Login failed. Please try again.")
                            f=True
                            
                    elif event.key == pygame.K_BACKSPACE:
                        text1 = text1[:-1]
                    else:
                        text1 += event.unicode
                else:
                    if event.key == pygame.K_RETURN:
                        # Check username and password against the database
                        cursor.execute("SELECT chat_id FROM users WHERE username=%s AND password=%s", (text1, text2))
                        result = cursor.fetchone()
                        if result:
                            chat_id = result[0]
                            print("Login successful! Chat ID:", chat_id)
                            db.close()
                            return chat_id
                        else:
                            print("Login failed. Please try again.")
                            f=True
                            
                    elif event.key == pygame.K_BACKSPACE:
                        text2 = text2[:-1]
                    else:
                        text2 += event.unicode

        screen.fill(white)

        



        # Input boxes
        txt_surface1 = font.render(text1, True, color)
        width1 = max(200, txt_surface1.get_width()+10)
        input_box1.w = width1
        screen.blit(txt_surface1, (input_box1.x+5, input_box1.y+5))
        pygame.draw.rect(screen, color, input_box1, 2)

        Un = font.render('USERNAME', True, color)
        screen.blit(Un, (input_box1.x, input_box1.y-25))
        pygame.draw.rect(screen, color, input_box1, 2)

        txt_surface2 = font.render(text2, True, color)
        width2 = max(200, txt_surface2.get_width()+10)
        input_box2.w = width2
        screen.blit(txt_surface2, (input_box2.x+5, input_box2.y+5))
        pygame.draw.rect(screen, color, input_box2, 2)

        Ps = font.render('PASSWORD', True, color)
        screen.blit(Ps, (input_box2.x, input_box2.y-25))
        pygame.draw.rect(screen, color, input_box2, 2)

        # Login button
        pygame.draw.rect(screen, black, login_button)
        button_font = pygame.font.Font("Aldrich-Regular.ttf", 20)
        button_text = button_font.render("Login", True, white)
        screen.blit(button_text, (370, 417))
        if f:
            screen.blit(pygame.font.Font("Aldrich-Regular.ttf", 28).render(" Enter UserName and Password correctly", True, (255,0,0)), (130,480))

        pygame.display.flip()




# Initialize pygame
pygame.init()

# Set up display
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Face Recognition Interface")

# Colors
white = (255, 255, 255)
black = (0, 0, 0)

# Font
font = pygame.font.Font("Aldrich-Regular.ttf", 36)
flag1=False
flag2=False




# Main loop
running = True
chat_id=login_interface(800,600)
while running:
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT or event.type == pygame.K_ESCAPE:
            running = False

        # Handle button clicks
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                x, y = event.pos
                # Check if the click is within the region of a button
                if x >= button1_x and x <= button1_x + button_width and y >= button1_y and y <= button1_y + button_height:
                    # Call the corresponding function
                    flag1=False
                    face_dataset()
                elif x >= button2_x and x <= button2_x + button_width and y >= button2_y and y <= button2_y + button_height:
                    #checking whether the image files already existed or not
                    folderOfImages="dataset"
                    if os.listdir(folderOfImages):
                        flag1=False
                        flag2=False
                        training()
                    else:
                        flag2=False
                        start_time = pygame.time.get_ticks()
                        duration = 4000  
                        current_time = pygame.time.get_ticks()
                        flag1=True
                        
                elif x >= button3_x and x <= button3_x + button_width and y >= button3_y and y <= button3_y + button_height:
                    Path_Of_Trainer= 'trainer.yml'

                    if os.path.exists(Path_Of_Trainer):
                        face_detect(chat_id)
                        flag1=False
                        flag2=False
                    else:
                        flag1=False
                        start_time = pygame.time.get_ticks()
                        duration = 4000  # 4 seconds in milliseconds
                        current_time = pygame.time.get_ticks()
                        flag2=True
    # Clear the screen
    screen.fill(white)

    # Drawing interface elements
    text = font.render("Face Recognition Interface", True, black)
    screen.blit(text, (width // 2 - text.get_width() // 2, 50))
    if flag2:
        
        if current_time - start_time < duration:
            print('yes')
            screen.blit(pygame.font.Font("Aldrich-Regular.ttf", 26).render("You not yet Trained the images to Detect", True, (255,0,0)), (35,450))
        else:
            flag2=False
    if flag1:
        
        if current_time - start_time < duration:
            print('yes')
            screen.blit(pygame.font.Font("Aldrich-Regular.ttf", 26).render("You not yet Uploaded the images to Train", True, (255,0,0)), (35,450))
        else:
            flag1=False
     

    # Define button dimensions and positions
    button_width, button_height = 150, 50
    button1_x, button1_y = 50, 200
    button2_x, button2_y = 50, 300
    button3_x, button3_y = 50, 400

    # Draw buttons
    pygame.draw.rect(screen, black, (button1_x, button1_y, button_width, button_height))
    pygame.draw.rect(screen, black, (button2_x, button2_y, button_width, button_height))
    pygame.draw.rect(screen, black, (button3_x, button3_y, button_width, button_height))
    
    # Button labels
    button_font = pygame.font.Font("Aldrich-Regular.ttf", 24)
    button1_text = button_font.render("Capture Faces", True, white)
    button2_text = button_font.render("Train Model", True, white)
    button3_text = button_font.render("Detect Faces", True, white)
    
    # Draw button labels
    screen.blit(button1_text, (button1_x + 10, button1_y + 10))
    screen.blit(button2_text, (button2_x + 10, button2_y + 10))
    screen.blit(button3_text, (button3_x + 10, button3_y + 10))

    # Update the display
    pygame.display.flip()

# Quit pygame

pygame.quit()

