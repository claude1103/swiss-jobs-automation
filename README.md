# 🇨🇭 Swiss Regulatory & AI Job Scraper

Welcome to your first automation! This project is designed to search for job opportunities in **Geneva, Vaud, Fribourg, and Zurich** that match specific criteria:
1. **FATCA & CRS Compliance / Regulations**
2. **AI (Artificial Intelligence) Governance, Law, or Banking**

The script is built to run automatically every day using **GitHub Actions** and save the results inside this repository in a file called `jobs_report.md`.

---

## 🛠️ Getting Started (Local Testing)

### 1. Run in Demo Mode (No keys needed)
We added a built-in **Demo Mode** so you can see how it works immediately!
1. Open your terminal or command prompt.
2. Run the script:
   ```bash
   python job_finder.py
   ```
3. A file called `jobs_report.md` will be created in this directory containing mock jobs. Open it up to see how it looks!

### 2. Run with Real Data (Using Adzuna keys)
Once you sign up for a free developer account at [developer.adzuna.com](https://developer.adzuna.com/), you'll receive an `app_id` and `app_key`.
To run the script locally with real data:
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Set your environment variables in your terminal (replace `your_id` and `your_key` with your real keys):
   * **Windows (Command Prompt):**
     ```cmd
     set ADZUNA_APP_ID=your_id
     set ADZUNA_APP_KEY=your_key
     python job_finder.py
     ```
   * **Windows (PowerShell):**
     ```powershell
     $env:ADZUNA_APP_ID="your_id"
     $env:ADZUNA_APP_KEY="your_key"
     python job_finder.py
     ```
   * **Mac / Linux:**
     ```bash
     export ADZUNA_APP_ID="your_id"
     export ADZUNA_APP_KEY="your_key"
     python job_finder.py
     ```

---

## ☁️ Deploying to the Cloud (GitHub Actions)

When you are ready to automate this so that it runs when your computer is off, follow these steps:

### 1. Create a Repository on GitHub
1. Go to [GitHub](https://github.com/) and log in.
2. Click **New Repository**.
3. Name it `swiss-jobs-automation`, keep it **Public** (or Private), and do NOT add a README, `.gitignore`, or license (we already have files here).
4. Click **Create repository**.

### 2. Push Code from Your PC to GitHub
Open your terminal inside this folder and run these commands to push the code:
```bash
git init
git add .
git commit -m "First commit: set up job scraper"
git branch -M main
git remote add origin https://github.com/YOUR_GITHUB_USERNAME/swiss-jobs-automation.git
git push -u origin main
```
*(Remember to replace `YOUR_GITHUB_USERNAME` with your actual GitHub username!)*

### 3. Add Your Adzuna Secrets to GitHub
To keep your API credentials safe:
1. In your GitHub repository webpage, go to **Settings** (top tab).
2. On the left sidebar, click **Secrets and variables** -> **Actions**.
3. Click the green button: **New repository secret**.
4. Add the first secret:
   * **Name:** `ADZUNA_APP_ID`
   * **Secret:** *(Paste your Adzuna App ID)*
5. Click **Add secret**.
6. Repeat the process to add a second secret:
   * **Name:** `ADZUNA_APP_KEY`
   * **Secret:** *(Paste your Adzuna App Key)*

### 4. Enable Workflow Write Permissions (Crucial!)
Since our automation writes the `jobs_report.md` back to your repository, we need to give GitHub Actions write permissions:
1. In your GitHub repository webpage, go to **Settings**.
2. On the left sidebar, click **Actions** -> **General**.
3. Scroll down to the **Workflow permissions** section.
4. Select **Read and write permissions**.
5. Click **Save**.

---

## 🎯 How to View the Daily Report
* The automation is set to run **every day at 8:00 AM UTC (10:00 AM Switzerland time)**.
* When it runs, it will update `jobs_report.md` in your repository.
* You can also run it manually at any time by going to the **Actions** tab in your GitHub repository, clicking **Scheduled Job Scraper** on the left, and clicking the **Run workflow** dropdown button!
