#ifndef promclient_h
#define promclient_h

#include <HTTPClient.h>
  #include <WiFiClientSecure.h>
#include "WriteRequest.h"
#include "PromDebug.h"

static const char PromUserAgent[] PROGMEM = "kphoen-prom-arduino/0.0.1";

class PromClient {
public:
    PromClient(WiFiClientSecure &client);
    ~PromClient();

    enum SendResult {
        SUCCESS,
        FAILED_RETRYABLE,
        FAILED_DONT_RETRY
    };

    void setUrl(const char* url);
    void setPath(const char* path);
    void setPort(uint16_t port);
    void setUser(const char* user);
    void setPass(const char* pass);

    void setDebug(Stream& stream);

    uint16_t getConnectCount();

    bool begin();
    SendResult send(WriteRequest& req);

    char* errmsg;

protected:
    Stream* _debug = nullptr;
    WiFiClientSecure& _wifi;
    Client* _client = nullptr;
    HTTPClient* _httpClient = nullptr;

    const char* _url;
    const char* _path;
    uint16_t _port;
    const char* _user;
    const char* _pass;
    uint16_t _connectCount = 0;

    SendResult _send(uint8_t* entry, size_t len);
};


#endif
