#currently it is under construction and not completed
import tkinter as tk
import cv2
from PIL import Image, ImageTk
from tkinter import messagebox
import threading

class VotingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Voting System")

        # Create a label for displaying the video feed
        self.video_label = tk.Label(root)
        self.video_label.pack(side=tk.LEFT)

        # Create a frame for voting options
        self.voting_frame = tk.Frame(root)
        self.voting_frame.pack(side=tk.RIGHT, padx=20)

        # Create a label and entry for Aadhar number
        self.label = tk.Label(self.voting_frame, text="Enter your Aadhar Number:")
        self.label.pack(pady=10)

        self.entry = tk.Entry(self.voting_frame)
        self.entry.pack(pady=10)

        # Create a button to start voting
        self.start_button = tk.Button(self.voting_frame, text="Start Voting", command=self.start_voting)
        self.start_button.pack(pady=20)

        # Initialize video capture
        self.video_capture = cv2.VideoCapture(0)
        self.is_voting_active = False  # Flag to check if voting is active
        self.voted_aadhars = set()  # Set to keep track of Aadhar numbers that have voted
        self.update_video()

    def update_video(self):
        ret, frame = self.video_capture.read()
        if ret:
            # Resize frame for faster processing (e.g., 320x240)
            frame = cv2.resize(frame, (320, 240))
            # Convert frame from BGR to RGB format
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # Convert to ImageTk format
            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)
            # Update label with new image
            self.video_label.imgtk = imgtk
            self.video_label.configure(image=imgtk)

        # Call this function again after 10 milliseconds
        self.video_label.after(10, self.update_video)

    def start_voting(self):
        if self.is_voting_active:  # Prevent starting voting again if already active
            return

        aadhar_number = self.entry.get()
        if not aadhar_number:
            messagebox.showwarning("Input Error", "Please enter your Aadhar number.")
            return

        if aadhar_number in self.voted_aadhars:
            messagebox.showwarning("Voting Error", "You have already voted!")
            return

        print(f"Aadhar Number: {aadhar_number}")

        # Start face detection in a separate thread
        threading.Thread(target=self.detect_face, args=(aadhar_number,), daemon=True).start()

    def detect_face(self, aadhar_number):
        F_detection = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        while True:
            ret, frame = self.video_capture.read()
            if not ret:
                print("Failed to capture frame")
                break
            
            # Resize frame for faster processing (e.g., 320x240)
            frame_resized = cv2.resize(frame, (320, 240))
            gray = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2GRAY)
            faces = F_detection.detectMultiScale(gray, 1.3, 5)

            if len(faces) > 0:  # If at least one face is detected
                break

            img = Image.fromarray(frame_resized)
            imgtk = ImageTk.PhotoImage(image=img)
            self.video_label.imgtk = imgtk
            self.video_label.configure(image=imgtk)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # After detecting a face successfully, show voting options and set flag
        self.is_voting_active = True
        self.show_voting_options(aadhar_number)

    def show_voting_options(self, aadhar_number):
        # Create buttons for voting options
        candidates = ["BJP", "Congress", "AAP", "NOTA"]
        
        for candidate in candidates:
            button = tk.Button(self.voting_frame, text=candidate,
                               command=lambda c=candidate: self.vote(c))
            button.pack(pady=5)

    def vote(self, candidate):
        messagebox.showinfo("Vote Recorded", f"Your vote for {candidate} has been recorded.")
        
        # Mark this Aadhar number as having voted
        aadhar_number = self.entry.get()
        if aadhar_number:
            self.voted_aadhars.add(aadhar_number)  # Add to the set of voted Aadhars
        
        # Stop video capture and reset application state after voting
        self.reset_voting()

    def reset_voting(self):
        """Reset the application state after voting."""
        
        # Release video capture and destroy any open windows
        if hasattr(self, 'video_capture'):
            self.video_capture.release()
        
        # Close the Tkinter window after voting is completed
        messagebox.showinfo("Thank You", "Thank you for participating in the election!")
        
        # Destroy the main window to close the application
        self.root.destroy()

    def __del__(self):
        if hasattr(self, 'video_capture'):
            self.video_capture.release()
            cv2.destroyAllWindows()

# Set up the main application window
root = tk.Tk()
app = VotingApp(root)
root.mainloop()