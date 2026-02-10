# OpenCode Phone Access Setup

## Goal: Access OpenCode from iPhone browser

### **Current Status:**
- ✅ OpenCode server running on Mac: `http://100.65.3.121:4096`
- ✅ Basic Auth: username `opencode`, password `Pncdfrwll25121997m@!`
- ✅ Listening on all interfaces (`*:4096`)
- ✅ Tailscale Serve HTTPS: `https://mihais-macbook-pro.taila9246e.ts.net`

### **Issue:**
Safari/Arc on iPhone shows "server not found" or doesn't connect.

## **Step-by-Step Solution:**

### **1. Verify Phone is on Tailscale Network**
```bash
# On your Mac, check if phone is connected:
/Applications/Tailscale.app/Contents/MacOS/Tailscale status
```
Look for your iPhone in the list. If not connected:
1. Open Tailscale app on iPhone
2. Log in with same account
3. Ensure it's connected (green indicator)

### **2. Test Connection from Phone**

**On iPhone Safari, try these URLs:**

#### **Option A: IP Address (Most Likely to Work)**
```
http://100.65.3.121:4096
```
- Should prompt for credentials
- Username: `opencode`
- Password: `Pncdfrwll25121997m@!`

#### **Option B: Embedded Credentials**
```
http://opencode:Pncdfrwll25121997m@!@100.65.3.121:4096
```

#### **Option C: Try Different Browser**
1. Install **Chrome** or **Firefox** on iPhone
2. Try the URLs above

### **3. Quick Diagnostic Test**

**On your Mac, run:**
```bash
# Test server accessibility
curl -v http://100.65.3.121:4096/health

# Check firewall (should show "opencode" listening)
sudo lsof -i :4096

# Test from phone perspective (simulate)
curl -u opencode:Pncdfrwll25121997m@! http://100.65.3.121:4096
```

### **4. Common Issues & Fixes**

#### **Issue 1: Phone not on Tailscale**
**Fix:** Ensure Tailscale app is running on iPhone and connected.

#### **Issue 2: Safari security restrictions**
**Fix:** 
1. Use Chrome/Firefox on iPhone
2. Or use embedded credentials URL (Option B above)

#### **Issue 3: DNS problems**
**Fix:** Use IP address (`100.65.3.121`) not domain name

#### **Issue 4: Port blocked**
**Fix:** Check macOS firewall:
```bash
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --listapps | grep opencode
```

### **5. Alternative Solutions**

#### **Solution A: Create iPhone Home Screen App**
1. Open `http://100.65.3.121:4096` in Safari
2. Tap Share button → "Add to Home Screen"
3. Opens like a native app

#### **Solution B: Use QR Code**
1. Generate QR code for: `http://opencode:Pncdfrwll25121997m@!@100.65.3.121:4096`
2. Scan with iPhone camera
3. Tap the link that appears

#### **Solution C: Bookmark with Credentials**
1. Create bookmark for embedded credentials URL
2. Tap bookmark whenever you need OpenCode

### **6. Test Now**

**On your iPhone right now:**
1. Open Safari
2. Go to: `http://100.65.3.121:4096`
3. Enter credentials when prompted

**If it doesn't work:**
1. Open Tailscale app → Ensure connected
2. Try Chrome/Firefox instead
3. Use embedded credentials URL

### **7. Files Created for You**

1. **`phone-access.html`** - Simple phone portal
2. **`opencode-access.html`** - Enhanced access portal  
3. **`test-safari.html`** - Safari compatibility tester
4. **`SETUP_GUIDE.md`** - Complete setup instructions

### **8. Success Indicators**

✅ **Working:** See OpenCode login page
✅ **Working:** Can enter credentials and access
✅ **Working:** Can create new coding sessions

❌ **Not Working:** "Server not found" → Check Tailscale
❌ **Not Working:** Connection timeout → Check firewall
❌ **Not Working:** No credential prompt → Use embedded URL

## **Final Recommendation:**

**Use this URL on iPhone:**
```
http://opencode:Pncdfrwll25121997m@!@100.65.3.121:4096
```

1. Copy this URL
2. Paste in iPhone Safari
3. Should open OpenCode directly

**If still not working:**
1. Check Tailscale connection on both devices
2. Try Chrome instead of Safari
3. Contact me with exact error message