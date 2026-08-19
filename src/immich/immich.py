import json
import logging
import urllib.request
import urllib.error
import ssl

class Immich:
    def __init__(self,url,apiKey,validCertOnly=True):
        # Setup logging
        self.logger = logging.getLogger(__name__ + '.' + self.__class__.__name__)

        if url is None or apiKey is None:
            raise AttributeError("Immich URL and API key are required to interact with server.")

        self.url=url
        self.apiKey=apiKey
        self.validCertOnly=validCertOnly

        if self.validCertOnly==False:
            # Create an unverified SSL context
            self.ssl_no_verify = ssl.create_default_context()
            self.ssl_no_verify.check_hostname = False
            self.ssl_no_verify.verify_mode = ssl.CERT_NONE



    def __generic__(self,endpoint,operation='GET',data=None):
        url = self.url.rstrip("/") + endpoint

        headers = {
            "x-api-key": self.apiKey,
            "Accept": "application/json",
        }

        # self.logger.debug(f"Immich request header: {headers}")

        body = None
        if data is not None:
            if operation == 'GET':
                url = url + '?' + urlencode(data)
            else:
                body = json.dumps(data).encode("utf-8")
                headers["Content-Type"] = "application/json"

        req = urllib.request.Request(
            url,
            data=body,
            headers=headers,
            method=operation,
        )


        # Try good SSL connection first, then a bad one if validCertOnly==False
        try:
            response = urllib.request.urlopen(req)

        except urllib.error.URLError as e:
            if not isinstance(e.reason, ssl.SSLCertVerificationError):
                # Error is not SSLCertVerificationError
                raise e
            else:
                # Server has an invalid SSL certificate, lets see if are allowed
                # to use talk to it anyway.
                if self.validCertOnly:
                    # No, not allowed
                    raise e
                else:
                    # Yes, lets talk anyway
                    response = urllib.request.urlopen(
                        req,
                        context=self.ssl_no_verify
                    )

        except urllib.error.HTTPError as e:
            err = e.read().decode()
            raise RuntimeError(f"HTTP {e.code}: {err}")

        # Decode response
        response = response.read().decode("utf-8")
        try:
            # Try to decode JSON
            return json.loads(response)
        except:
            # Failed, so return raw response
            return None if not response else response



    def get(self,endpoint,data=None):
        return self.__generic__(endpoint,'GET',data)

    def put(self,endpoint,data=None):
        return self.__generic__(endpoint,'PUT',data)

    def post(self,endpoint,data=None):
        return self.__generic__(endpoint,'POST',data)

    def patch(self,endpoint,data=None):
        return self.__generic__(endpoint,'PATCH',data)

    def delete(self,endpoint,data=None):
        return self.__generic__(endpoint,'DELETE',data)

    def albums(self):
        return self.get('/albums')

    def assets(self,filters=None):
        """
        filters is a dict() with parameters as the Request struct at
        https://api.immich.app/endpoints/search/searchAssets

        Returns a list of all assets that match filters, and their attributes as
        known by Immich.
        """
        assets = None
        nextPage = 1

        if (basicFilter:=filters) is None:
            basicFilter = dict(order='asc')

        while True:
            page=self.post(
                '/search/metadata',
                basicFilter | dict(page=nextPage)
            )['assets']

            logging.debug("{} items in assets page {}".format(page['count'],nextPage))

            if assets is None:
                assets = page['items']
            else:
                assets += page['items']

            if (nextPage:=page['nextPage']) is None:
                break

            nextPage=int(nextPage)

        return assets
