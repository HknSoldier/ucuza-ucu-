# ⚖️ SNIPER V20 - LEGAL & COMPLIANCE DOCUMENTATION

## 🔴 CRITICAL: READ BEFORE USE

This document outlines the **legal boundaries**, **ethical guidelines**, and **security measures** for SNIPER V20 - GHOST PROTOCOL.

---

## ✅ WHAT THIS BOT **DOES**

### **Legal & Ethical Uses:**

1. **Price Observation**
   - Monitors publicly available flight prices
   - Compares prices across currencies
   - Tracks price trends over time

2. **Link Generation**
   - Creates search URLs for Google Flights
   - Creates search URLs for Google Hotels
   - **No direct booking or automation**

3. **Information Aggregation**
   - Scrapes public travel blogs (respecting robots.txt)
   - Aggregates deal information
   - Sends notifications to **your own** Telegram

4. **Currency Arbitrage Detection**
   - Compares prices in multiple currencies
   - Uses real exchange rates from public APIs
   - Identifies legitimate pricing differences

---

## ❌ WHAT THIS BOT **DOES NOT DO**

### **Prohibited Actions (By Design):**

1. **NO Purchase Automation**
   - ❌ Does not automate bookings
   - ❌ Does not fill out forms
   - ❌ Does not process payments
   - ❌ Does not submit reservations

2. **NO Captcha Bypassing**
   - ❌ No 2captcha integration
   - ❌ No anti-captcha services
   - ❌ No captcha solving libraries
   - ❌ No OCR-based captcha breaking

3. **NO Aggressive Scraping**
   - ❌ No parallel requests (sequential only)
   - ❌ No DOM scraping of flight booking sites
   - ❌ No browser automation (Selenium/Playwright)
   - ❌ No cloudflare bypass attempts

4. **NO ToS Violations**
   - ❌ Does not circumvent access controls
   - ❌ Does not spoof identities
   - ❌ Does not exploit vulnerabilities
   - ❌ Does not violate rate limits intentionally

---

## 🛡️ SECURITY MEASURES

### **Anti-Detection (Ethical)**

These measures are for **rate limiting compliance**, not evasion:

```python
# ✅ ETHICAL: Simulates normal user behavior
User-Agent rotation       # Appears as different browsers
Random delays (2-12s)     # Human-like browsing speed
Sequential requests       # No spam/flooding
Rate limiting             # Max 10 requests/session

# ❌ NOT INCLUDED: Evasion techniques
No proxy rotation         # Honest IP address
No VPN cycling            # No IP hiding
No TOR usage              # Transparent origin
No fingerprint spoofing   # Basic headers only
```

### **Data Privacy**

- ✅ No personal data collected
- ✅ No user tracking
- ✅ No data sold or shared
- ✅ Price data only (public information)
- ✅ Telegram messages sent to **your bot only**

### **API Security**

- ✅ Secrets stored in GitHub (encrypted)
- ✅ No hardcoded credentials
- ✅ HTTPS-only communication
- ✅ No sensitive data in logs

---

## 📋 TERMS OF SERVICE COMPLIANCE

### **Google Flights / Hotels**

**What we do:**
- ✅ Generate search links (permitted)
- ✅ Direct users to official sites
- ✅ No automated interactions

**What we DON'T do:**
- ❌ Scrape Google Flights directly
- ❌ Automate form submissions
- ❌ Bypass any restrictions

**Reference:** Google's [Terms of Service](https://policies.google.com/terms)

### **Travel Blog Scraping**

**Compliance measures:**
- ✅ Respects robots.txt
- ✅ Rate-limited requests
- ✅ Human-like delays
- ✅ Public information only

**Specific to ucuzaucak.net:**
- Only scrapes publicly visible blog posts
- Does not access member-only content
- Does not bypass paywalls

---

## 🚨 RISK WARNINGS

### **For Users**

1. **Price Accuracy**
   - ⚠️ Prices are estimates (verify before booking)
   - ⚠️ Currency conversions may vary
   - ⚠️ Deals expire quickly

2. **Booking Responsibility**
   - ⚠️ You are responsible for all bookings
   - ⚠️ Verify prices on official sites
   - ⚠️ Check visa requirements
   - ⚠️ Review cancellation policies

3. **Technical Risks**
   - ⚠️ GitHub Actions may fail
   - ⚠️ APIs may change
   - ⚠️ Notifications may be delayed

### **For Developers**

1. **Code Modifications**
   - ⚠️ Do NOT add browser automation
   - ⚠️ Do NOT integrate captcha solvers
   - ⚠️ Do NOT implement purchase automation
   - ⚠️ Do NOT bypass rate limits

2. **API Usage**
   - ⚠️ Respect free tier limits
   - ⚠️ Monitor API quotas
   - ⚠️ Handle errors gracefully

---

## 📝 DISCLAIMER

```
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.

THIS BOT IS FOR EDUCATIONAL AND PRICE OBSERVATION PURPOSES ONLY.

USERS ARE SOLELY RESPONSIBLE FOR:
- Ensuring compliance with all applicable laws
- Respecting all terms of service
- Verifying all prices before booking
- Any consequences of misuse

THE AUTHORS AND CONTRIBUTORS ARE NOT RESPONSIBLE FOR:
- Financial losses
- Booking errors
- ToS violations by users
- Legal consequences of misuse
```

---

## 🔧 PRODUCTION API REQUIREMENTS

### **Required for Real Flight Data**

To use REAL prices (not mock data), you MUST use **official APIs**:

#### **Option 1: Amadeus API** ✅ RECOMMENDED

- **Legal:** Official airline data provider
- **Cost:** Free tier (2000 calls/month)
- **Sign up:** https://developers.amadeus.com
- **Compliance:** Fully licensed and legitimate

#### **Option 2: Kiwi.com API** ✅ RECOMMENDED

- **Legal:** Official OTA API
- **Cost:** Free tier available
- **Sign up:** https://tequila.kiwi.com/portal/login
- **Compliance:** Licensed and legitimate

#### **Option 3: Skyscanner API** ✅ RECOMMENDED (Partner Only)

- **Legal:** Official meta-search API
- **Cost:** Free for partners
- **Apply:** https://partners.skyscanner.net
- **Compliance:** Requires business verification

### **NOT PERMITTED** ❌

Do NOT use:
- ❌ Selenium/Playwright for price scraping
- ❌ Unofficial "scraper" libraries
- ❌ Reverse-engineered APIs
- ❌ Proxy services for ban evasion

---

## 📊 RATE LIMITING POLICY

### **Self-Imposed Limits**

```yaml
Intelligence Layer (Blog Scraping):
  - Max 10 requests per session
  - 2-5 second delays between requests
  - 30-60 second cooldown after 10 requests

Analysis Layer (Price Checks):
  - Sequential only (no parallel)
  - 5-12 second delays between routes
  - 1.5-3 second delays between currencies
  - Max 25 routes per scan

Notification Layer:
  - Standard Telegram API limits
  - No bulk messaging
```

### **GitHub Actions Limits**

- 4 scheduled runs per day
- 45-minute timeout per run
- Sequential execution (no concurrency)

---

## 🤝 ETHICAL GUIDELINES

### **Do's**

✅ Use for personal deal hunting  
✅ Share with friends and family  
✅ Contribute improvements  
✅ Report bugs and issues  
✅ Follow all guidelines  

### **Don'ts**

❌ Resell as a service  
❌ Use for commercial gain without permission  
❌ Modify to violate ToS  
❌ Add malicious features  
❌ Overwhelm servers  

---

## 📞 REPORTING VIOLATIONS

If you discover someone using this code to:
- Violate terms of service
- Bypass security measures
- Automate bookings
- Solve captchas
- Engage in fraud

**Please report to:**
- GitHub repository issues
- abuse@github.com (for serious violations)

---

## 🔄 VERSION COMPLIANCE

Current version: **V20 - GHOST PROTOCOL**

**Compliance Audit Date:** January 2026

**Next Review:** Quarterly

**Changes Log:**
- ✅ Removed all browser automation
- ✅ Removed captcha solving references
- ✅ Added sequential execution
- ✅ Added rate limiting
- ✅ Added legal disclaimers

---

## ⚖️ JURISDICTION

This software is provided for use in jurisdictions where:
- Price comparison is legal
- Web scraping of public data is permitted
- Currency arbitrage is not restricted

**Users must verify local laws before use.**

---

## 📧 CONTACT

For legal inquiries:
- Create a GitHub issue with tag `legal`
- Email: [your-email] (if applicable)

For compliance questions:
- Review this document first
- Check README.md
- Open a discussion on GitHub

---

**Last Updated:** January 13, 2026  
**Version:** 20.0 (GHOST PROTOCOL)  
**Status:** ✅ Compliance Verified

---

## 🏛️ LICENSE

MIT License

Copyright (c) 2026 SNIPER V20 Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software **FOR PERSONAL USE ONLY**, subject to the following conditions:

- Must comply with all applicable laws
- Must respect all terms of service
- Must not use for automated booking
- Must not bypass security measures

---

**Remember: With great power comes great responsibility. Use ethically! 🙏**
