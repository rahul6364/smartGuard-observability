# 🚨 Slack Notification Setup Guide

This guide will help you set up Slack notifications for critical issues in the SmartGuard AI Dashboard.

## Quick Setup

### 1. Get Your Slack Webhook URL

1. Go to your Slack workspace
2. Navigate to **Apps** → **Incoming Webhooks**
3. Click **Add to Slack**
4. Choose the channel where you want alerts (e.g., #dev-alerts, #monitoring)
5. Copy the webhook URL (looks like: `https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX`)

### 2. Add to Environment Variables

Add your Slack webhook URL to the `.env` file:

```env
# Slack Integration
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK
```

### 3. Test the Integration

1. Start the application:
   ```bash
   python start_dev.py
   ```

2. Open the dashboard: http://localhost:8501

3. Go to the **🚨 Alerts** section

4. Click the **🧪 Test Slack Alert** button

5. Check your Slack channel for the test message

## What You'll Receive

### Test Alert Format
```
🧪 Test Alert from SmartGuard AI Dashboard

This is a test notification to verify Slack integration is working correctly.

Timestamp: 2024-01-15T10:30:00.000Z
```

### Critical Error Alerts
When critical errors are detected, you'll receive formatted alerts with:
- 🔴 **Service name** and **severity level**
- ⏰ **Timestamp** of the issue
- 📝 **Raw log data** for debugging
- 🔗 **Link to dashboard** for immediate access
- 🚨 **Status indicator** requiring immediate attention

## Automatic Alerting

The system automatically sends Slack notifications when:
- **ERROR** level logs are detected
- Critical keywords are found in log analysis:
  - error, critical, fatal, exception, failed
  - down, outage, timeout, connection refused
  - database error, memory leak, disk full

## Troubleshooting

### Common Issues

1. **"Slack webhook URL not configured"**
   - Check that `SLACK_WEBHOOK_URL` is set in your `.env` file
   - Verify the URL format is correct

2. **"Failed to send test alert"**
   - Check your internet connection
   - Verify the webhook URL is still valid
   - Check if Slack has rate limits

3. **No alerts received**
   - Ensure the webhook URL is correct
   - Check the Slack channel permissions
   - Verify the webhook is still active

### Testing Commands

You can also test via API:
```bash
curl -X POST http://localhost:8000/test-slack-alert
```

## Customization

### Alert Frequency
The system sends alerts for every ERROR level log. To reduce frequency, you can modify the alert logic in `backend/smartguard_integration.py`.

### Alert Format
Customize the Slack message format in `backend/smartguard.py` in the `send_alert()` function.

### Channel Selection
Change the target channel by updating the webhook URL in your Slack app settings.

## Security Notes

- Keep your webhook URL secure
- Don't commit the `.env` file to version control
- Consider using environment variables in production
- Regularly rotate webhook URLs if needed

---

**Your SmartGuard AI Dashboard is now ready to send critical alerts directly to your Slack channel!** 🎉
