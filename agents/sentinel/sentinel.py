import os
import json
import logging
from datetime import datetime
from dotenv import load_dotenv
import anthropic

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('sentinel')


class SentinelAgent:
    def __init__(self):
        self.client = anthropic.Anthropic(
            api_key=os.getenv('ANTHROPIC_API_KEY')
        )
        self.model = "claude-opus-4-5"
        logger.info("Sentinel agent initialized")

    def analyze_alert(self, alert: dict) -> dict:
        logger.info(f"Analyzing alert: {alert['name']}")

        prompt = f"""
        You are an expert cloud operations engineer analyzing infrastructure alerts.
        
        Analyze this alert and respond with ONLY a JSON object, nothing else:
        
        Alert Details:
        - Name: {alert['name']}
        - Service: {alert['service']}
        - Metric: {alert['metric']}
        - Current Value: {alert['value']}
        - Threshold: {alert['threshold']}
        - Environment: {alert['environment']}
        
        Respond with exactly this JSON structure:
        {{
            "severity": "LOW or MEDIUM or HIGH",
            "summary": "one sentence explaining what is happening",
            "impact": "one sentence explaining business impact",
            "recommended_action": "one sentence on what to do",
            "needs_immediate_attention": true or false
        }}
        """

        message = self.client.messages.create(
            model=self.model,
            max_tokens=500,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        response_text = message.content[0].text
        clean_response = response_text.strip()
        if clean_response.startswith("```"):
            clean_response = clean_response.split("```")[1]
            if clean_response.startswith("json"):
                clean_response = clean_response[4:]
        clean_response = clean_response.strip()
        analysis = json.loads(clean_response)
        analysis['alert'] = alert
        analysis['analyzed_at'] = datetime.now().isoformat()

        logger.info(f"Severity determined: {analysis['severity']}")
        return analysis


def simulate_alerts():
    return [
        {
            "name": "High CPU Usage",
            "service": "payment-api",
            "metric": "cpu_percentage",
            "value": "95%",
            "threshold": "80%",
            "environment": "production"
        },
        {
            "name": "Disk Space Warning",
            "service": "database-server",
            "metric": "disk_usage",
            "value": "72%",
            "threshold": "70%",
            "environment": "production"
        },
        {
            "name": "Pod Restart Detected",
            "service": "auth-service",
            "metric": "pod_restart_count",
            "value": "15 restarts in 5 minutes",
            "threshold": "3 restarts in 5 minutes",
            "environment": "production"
        }
    ]


if __name__ == "__main__":
    sentinel = SentinelAgent()
    alerts = simulate_alerts()

    print("\n" + "="*60)
    print("CLOUDOPS-AI — SENTINEL AGENT")
    print("="*60)

    for alert in alerts:
        print(f"\nProcessing: {alert['name']}")
        print("-" * 40)

        analysis = sentinel.analyze_alert(alert)

        print(f"Severity:   {analysis['severity']}")
        print(f"Summary:    {analysis['summary']}")
        print(f"Impact:     {analysis['impact']}")
        print(f"Action:     {analysis['recommended_action']}")
        print(f"Immediate:  {analysis['needs_immediate_attention']}")