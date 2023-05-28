from rest_framework.views import APIView
from rest_framework.response import Response
from django.conf import settings
from google.oauth2 import credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from django.shortcuts import redirect
from django.urls import reverse
import urllib.parse
from django.shortcuts import render


class GoogleCalendarInitView(APIView):
    def get(self, request):
        authorization_url = 'https://accounts.google.com/o/oauth2/auth'
        
        # Construct the required parameters
        params = {
            'client_id': settings.GOOGLE_CLIENT_ID,
            'redirect_uri': request.build_absolute_uri(reverse('google_calendar_redirect')),
            'response_type': 'code',
            'scope': 'https://www.googleapis.com/auth/calendar.readonly',
        }
        
        # Append the parameters to the authorization URL
        authorization_url += '?' + urllib.parse.urlencode(params)

        # Render the HTML template with the authorization URL
        return render(request, 'google_auth.html', {'authorization_url': authorization_url})




class GoogleCalendarRedirectView(APIView):
    def get(self, request):
        authorization_code = request.GET.get('code')

        flow = InstalledAppFlow.from_client_secrets_file(
            settings.GOOGLE_CLIENT_SECRET_FILE,
            scopes=['https://www.googleapis.com/auth/calendar.readonly'],
            redirect_uri=settings.GOOGLE_REDIRECT_URI,  # Use the configured redirect URI
        )
        flow.fetch_token(authorization_response=request.build_absolute_uri())

        credentials = flow.credentials
        access_token = credentials.token

        # Retrieve list of events using the access_token
        service = build('calendar', 'v3', credentials=credentials)

        events_result = service.events().list(calendarId='primary').execute()
        events = events_result.get('items', [])

        event_data = []
        for event in events:
            event_data.append({
                'summary': event.get('summary', ''),
                'start_time': event['start'].get('dateTime', event['start'].get('date')),
                'end_time': event['end'].get('dateTime', event['end'].get('date')),
            })

        # Render the HTML template with the events data
        return render(request, 'events.html', {'access_token': access_token, 'events': event_data})

