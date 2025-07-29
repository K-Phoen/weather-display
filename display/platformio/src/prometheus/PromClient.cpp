#include "prometheus/PromClient.h"

PromClient::PromClient(WiFiClientSecure &client) : _wifi(client) {};
PromClient::~PromClient() {
    if (_httpClient) {
        delete _httpClient;
    }
};

void PromClient::setUrl(const char* url) {
    _url = url;
};
void PromClient::setPath(const char* path) {
    _path = path;
};
void PromClient::setPort(uint16_t port) {
    _port = port;
};
void PromClient::setUser(const char* user) {
    _user = user;
};
void PromClient::setPass(const char* pass) {
    _pass = pass;
};


void PromClient::setDebug(Stream& stream) {
    _debug = &stream;
};

uint16_t PromClient::getConnectCount() {
    return _connectCount;
}

bool PromClient::begin() {
    errmsg = nullptr;
    if (!_url) {
        errmsg = (char*)"you must set a url with setUrl()";
        return false;
    }
    if (!_path) {
        errmsg = (char*)"you must set a path with setPath()";
        return false;
    }
    if (!_port) {
        errmsg = (char*)"you must set a port with setPort()";
        return false;
    }

    // Create the HttpClient
    _httpClient = new HTTPClient();
    _httpClient->setTimeout(15000);
    _httpClient->setReuse(true);
     if (_user && _pass) {
        _httpClient->setAuthorization(_user, _pass);
    }

    return _httpClient->begin(this->_wifi, this->_url, this->_port, this->_path);
};

PromClient::SendResult PromClient::send(WriteRequest& req) {
    errmsg = nullptr;
    uint8_t buff[req.getBufferSize()] = { 0 };
    int16_t len = req.toSnappyProto(buff);
    if (len <= 0) {
        errmsg = req.errmsg;
        return PromClient::SendResult::FAILED_DONT_RETRY;
    }
    return _send(buff, len);
};

PromClient::SendResult PromClient::_send(uint8_t* entry, size_t len) {
    DEBUG_PRINTLN("Sending To Prometheus");

    _httpClient->addHeader("User-Agent", PromUserAgent);
   
    int statusCode = _httpClient->POST(entry, len);
    int statusClass = statusCode / 100;
    if (statusClass == 2) {
        DEBUG_PRINTLN("Prom Send Succeeded");
    }
    else if (statusClass == 4) {
        DEBUG_PRINT("Prom Send Failed with code: ");
        DEBUG_PRINTLN(statusCode);
        errmsg = (char*)"Failed to send to prometheus, 4xx response";
        return PromClient::SendResult::FAILED_DONT_RETRY;
    }
    else {
        DEBUG_PRINT("Prom Send Failed with code: ");
        DEBUG_PRINTLN(statusCode);
        errmsg = (char*)"Failed to send to prometheus, 5xx or unexpected status code";
        return PromClient::SendResult::FAILED_RETRYABLE;
    }
    return PromClient::SendResult::SUCCESS;
};
