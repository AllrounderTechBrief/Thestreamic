# The Streamic

An Apple-inspired news aggregation website for broadcast technology updates.

## 🎯 Features

- **Apple.com Design Language**: Clean, minimal, professional aesthetic
- **5 Cards Per Row Layout**: Responsive grid layout (5→4→3→2→1 cards based on screen size)
- **RSS-Based Content**: Automated daily updates from industry sources
- **Static Site**: All rendering happens at build time via GitHub Actions
- **SEO Optimized**: Proper meta tags, semantic HTML, canonical URLs
- **Mobile Responsive**: Works beautifully on all devices
- **Cookie Consent**: GDPR-compliant cookie management
- **Legal Pages**: Complete privacy policy, terms, disclaimer, copyright notices

## 📁 Project Structure

```
streamic-website/
├── .github/
│   └── workflows/
│       └── rss.yml          # GitHub Actions workflow
├── assets/
│   ├── logo.png             # Streamic logo
│   └── fallback.jpg         # Fallback image for articles
├── data/                    # Generated JSON feeds (created by build.py)
│   ├── streaming-tech.json
│   ├── newsroom.json
│   ├── playout.json
│   ├── ip-video.json
│   ├── cloud-ai.json
│   └── audio.json
├── index.html               # Homepage
├── streaming-tech.html      # Category pages (6 total)
├── newsroom.html
├── playout.html
├── ip-video.html
├── cloud-ai.html
├── audio.html
├── about.html               # About page
├── contact.html             # Contact page
├── privacy.html             # Legal pages
├── terms.html
├── cookies.html
├── disclaimer.html
├── copyright.html
├── rss-policy.html
├── style.css                # Main stylesheet
├── app.js                   # Homepage loader
├── category.js              # Category page loader
├── cookies.js               # Cookie consent handler
└── build.py                 # RSS aggregator script
```

## 🚀 Deployment Instructions

### 1. Create a New GitHub Repository

```bash
# Create a new repository on GitHub (e.g., "thestreamic")
# Then clone it locally
git clone https://github.com/YOUR_USERNAME/thestreamic.git
cd thestreamic
```

### 2. Copy All Files

Copy all files from this package into your repository:

```bash
# Copy all files from streamic-website/ to your repo
cp -r /path/to/streamic-website/* .
```

### 3. Initial Commit

```bash
git add .
git commit -m "Initial commit - The Streamic website"
git push origin main
```

### 4. Enable GitHub Pages

1. Go to your repository on GitHub
2. Click **Settings** → **Pages**
3. Under **Source**, select **Deploy from a branch**
4. Select **main** branch and **/ (root)** folder
5. Click **Save**

### 5. Run Initial RSS Build

1. Go to **Actions** tab in your repository
2. Click on **Update RSS Feeds** workflow
3. Click **Run workflow** → **Run workflow**
4. Wait for it to complete (creates data/*.json files)

### 6. Access Your Site

Your site will be live at: `https://YOUR_USERNAME.github.io/thestreamic/`

## 🔄 How It Works

### RSS Aggregation

The `build.py` script:
1. Fetches RSS feeds from broadcast technology publishers
2. Parses XML/RSS data
3. Extracts headlines, links, sources, and images
4. Generates JSON files in `data/` directory
5. Runs automatically every day at 6:00 AM UTC via GitHub Actions

### Content Display

- **Homepage** (`index.html`): Shows 10 items from each category
- **Category Pages**: Show 20 items initially, then "Load More" button for 15 more at a time
- **5 Cards Per Row**: Responsive grid automatically adjusts for screen size

### Styling

Apple-inspired design with:
- SF Pro Display font family
- Clean card-based layout
- Subtle hover animations
- Consistent spacing and typography
- Minimalist color palette (#0071e3 blue, #1d1d1f text, #f5f5f7 background)

## 🛠️ Customization

### Add New RSS Feed

Edit `build.py` and add sources to the appropriate category:

```python
streaming_sources = [
    {"url": "https://example.com/feed.xml", "label": "Example Source"},
    # Add your source here
]
```

### Change Number of Cards Per Row

Edit `style.css` and modify the `.card-grid` rules:

```css
.card-grid {
  grid-template-columns: repeat(5, 1fr);  /* Change 5 to your desired number */
}
```

### Update Logo

Replace `assets/logo.png` with your own logo (recommended size: 48px height)

### Modify Colors

Edit CSS variables in `style.css`:

```css
:root {
  --apple-blue: #0071e3;      /* Primary color */
  --apple-text: #1d1d1f;      /* Text color */
  --apple-gray: #6e6e73;      /* Secondary text */
  /* ... */
}
```

## 📧 Contact Configuration

Update the email in:
- `contact.html` (contact form)
- All legal pages (privacy.html, terms.html, etc.)

Current email: `itabmum@gmail.com`

## 📝 Content Sources

Currently aggregating from:
- **TV Technology** - Industry news and technical updates
- **Broadcasting & Cable** - Broadcasting industry news
- **Streaming Media** - Streaming technology news
- **Sports Video Group** - Sports production technology
- **IBC** - International Broadcasting Convention news
- **Pro Sound Network** - Professional audio technology

## 🔒 Legal Compliance

Includes all standard legal pages:
- **Privacy Policy**: GDPR-compliant privacy information
- **Terms & Conditions**: Usage terms
- **Cookie Policy**: Cookie usage and management
- **Disclaimer**: Liability limitations
- **Copyright Notice**: Intellectual property information
- **RSS Policy**: RSS aggregation practices

## 🎨 Design Credits

Design inspired by Apple.com with modifications for news aggregation.

## 📄 License

Website code and design © 2026 The Streamic. All aggregated content belongs to respective publishers.

## 🤝 Contributing

Created by Prerak Mehta. For feedback or collaboration: itabmum@gmail.com

---

**Note**: This is a static website that requires GitHub Pages or similar hosting. RSS feeds are updated automatically via GitHub Actions.
