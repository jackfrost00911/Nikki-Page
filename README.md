 # Nikki-Page

Nikki-Page is a modern, elegant personal website for Nikki Squirts â€” a luxury companion and industry commentator based in Reno, Nevada. This site presents Nikkiâ€™s services, rates, gallery, blog, and allows visitors to book appointments directly.

## Features

- **Responsive Design:** Clean and stylish layout using modern CSS, Google Fonts, and CSS libraries.
- **Sticky Navigation:** Easy-to-use navigation bar for quick access to all sections.
- **About Section:** Introduction and background information about Nikki.
- **Services & Rates:** Clear list of services offered and donation rates, with detailed explanations.
- **Booking System:** Interactive booking form using [Flatpickr](https://flatpickr.js.org/) date and time picker, with unavailable dates fetched from a backend and live updates.
- **Blog:** Industry insights, professionalism tips, and wellness advice written by Nikki.
- **Gallery:** Photo gallery using [GLightbox](https://biati-digital.github.io/glightbox/) for fullscreen viewing.
- **Newsletter Signup:** Quick signup for email updates.
- **Accessibility:** Focused on clarity and usability for all users.

## Technology Stack

- **HTML5 & CSS3:** Responsive, accessible markup and styles.
- **JavaScript:** Handles booking, calendar, newsletter signup, and reveal animations.
- **Flatpickr:** Interactive date/time picker for reservations.
- **GLightbox:** Gallery for image previews.
- **Backend:** Designed to work with a Flask or PHP backend for booking and availability APIs (see below).

## Booking System Details

- Unavailable dates/times are fetched from a backend API (`/api/availability` and `/get_bookings.php`).
- Form submissions are sent to a booking API endpoint (`/save_booking.php`).
- The booking form includes required fields (name, email, service selection, date/time), and optional details (phone, location, special requests).
- Booking status feedback is provided to the user after submission.

## How to Run Locally

1. **Clone the repository:**
   ```bash
   git clone https://github.com/jackfrost00911/Nikki-Page.git
   cd Nikki-Page
   ```

2. **Open `index.html` in your browser:**
   - You can use Live Server in VSCode or simply double-click the file.

3. **Set up the backend:**
   - The booking and calendar features rely on backend APIs (`/api/availability`, `/get_bookings.php`, `/save_booking.php`).
   - You can implement these in Flask (Python) or PHP.
   - Example Flask endpoints:
     - `/api/availability`: returns unavailable dates in JSON.
     - `/save_booking.php`: accepts POST requests and stores bookings, returns status.

4. **Configure API URLs:**
   - Update the API URLs in `index.html` if your backend is hosted elsewhere or uses different endpoints.

5. **Image Assets:**
   - Gallery and hero images are loaded from the repository. Ensure images are present in the repo or update URLs as needed.

## Customization

- **Blog Posts:** Edit or add new `<article>` blocks in the blog section of `index.html`.
- **Gallery:** Add new images by updating the gallery section.
- **Services/Rates:** Adjust offerings or rates in the HTML.
- **Newsletter:** Integrate with your preferred mailing list provider in the newsletter section.

## Accessibility & Design

- Clean, readable fonts (Playfair Display + Inter).
- Color palette for elegance and readability.
- Responsive layout for mobile and desktop.
- All interactive elements are keyboard accessible.

## License

This project is intended for personal use by Nikki Squirts and may not be redistributed or used for commercial purposes without permission.

---

**Contact and Support**

For questions or support, please reach out via the booking form or contact details provided on the website.
