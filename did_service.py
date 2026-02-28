import os
import requests
import json
import base64

class DIDService:
    def __init__(self):
        self.api_key = os.environ.get("DID_API_KEY", "").strip()
        self.base_url = "https://api.d-id.com"
        
        # Prepare headers
        if self.api_key:
            # D-ID usually expects Basic Auth with "API_USER:API_PASSWORD" 
            # or just the key depending on how it was generated.
            # The user provided 'Basic <YOUR KEY>' in their curl example.
            if ":" not in self.api_key and not self.api_key.startswith("Basic "):
                # If it's just a raw key, we might need to encode it if it's the USER:PASS format
                # But usually D-ID keys from the studio are already the full string or need base64.
                # Let's assume the user will paste the 'Basic ...' string or the raw 'user:pass'
                pass
            
            self.headers = {
                "Authorization": self.api_key if self.api_key.startswith("Basic ") else f"Basic {self.api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
        else:
            self.headers = {}

    def is_configured(self):
        return bool(self.api_key)

    def create_agent(self, name="Amber", presenter_id="v2_public_Amber@0zSz8kflCN", voice_id="en-US-JennyMultilingualV2Neural"):
        """Creates a D-ID agent if one doesn't exist or returns the config."""
        url = f"{self.base_url}/agents"
        payload = {
            "preview_name": name,
            "presenter": {
                "type": "clip",
                "presenter_id": presenter_id,
                "voice": {
                    "type": "microsoft",
                    "voice_id": voice_id
                }
            },
            "llm": {
                "provider": "openai",
                "model": "gpt-4.1-mini",
                "instructions": "you are a helpful assistant"
            }
        }
        
        try:
            resp = requests.post(url, json=payload, headers=self.headers, timeout=15)
            if resp.status_code in [200, 201]:
                return resp.json()
            else:
                print(f"[D-ID] Create Agent Failed: {resp.status_code} - {resp.text}")
                return None
        except Exception as e:
            print(f"[D-ID] Error creating agent: {e}")
            return None

    def get_agent(self, agent_id):
        """Gets agent details, including idle_video."""
        url = f"{self.base_url}/agents/{agent_id}"
        try:
            resp = requests.get(url, headers=self.headers, timeout=10)
            if resp.status_code == 200:
                return resp.json()
            return None
        except Exception as e:
            print(f"[D-ID] Error getting agent: {e}")
            return None

    def list_agents(self):
        """Lists all agents available."""
        url = f"{self.base_url}/agents"
        try:
            resp = requests.get(url, headers=self.headers, timeout=10)
            if resp.status_code == 200:
                return resp.json()
            return []
        except Exception as e:
            print(f"[D-ID] Error listing agents: {e}")
            return []

    def chat(self, agent_id, message, session_id=None):
        """Sends a message to the agent and gets a response."""
        # Note: D-ID Agents API for chat might vary (streaming vs clips)
        # Based on the user's provided snippet, they only showed agent creation and status.
        # For a real-time feel, we might need the 'streams' API or the 'chats' endpoint.
        # However, I will start by implementing a basic clip generation if that's what's supported.
        
        url = f"{self.base_url}/agents/{agent_id}/chat"
        payload = {
            "input": message,
            "stream": False # Set to true for streaming if supported by frontend
        }
        if session_id:
            payload["session_id"] = session_id

        try:
            resp = requests.post(url, json=payload, headers=self.headers, timeout=20)
            if resp.status_code in [200, 201]:
                return resp.json()
            else:
                print(f"[D-ID] Chat Failed: {resp.status_code} - {resp.text}")
                return None
        except Exception as e:
            print(f"[D-ID] Error in chat: {e}")
            return None
