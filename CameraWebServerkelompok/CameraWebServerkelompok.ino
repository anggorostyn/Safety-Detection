#include "esp_camera.h"
#include <WiFi.h>
#include "esp_http_server.h"

// Pilih model kamera
#define CAMERA_MODEL_AI_THINKER
#include "camera_pins.h"

// WiFi
const char *ssid = "Jaringan Sibulek";
const char *password = "Juntak060466";

// Pin Output
#define LED_HIJAU 12
#define LED_MERAH 13
#define BUZZER     2

// Konstanta streaming
#define PART_BOUNDARY "123456789000000000000987654321"
static const char* _STREAM_CONTENT_TYPE = "multipart/x-mixed-replace;boundary=" PART_BOUNDARY;
static const char* _STREAM_BOUNDARY = "\r\n--" PART_BOUNDARY "\r\n";
static const char* _STREAM_PART = "Content-Type: image/jpeg\r\nContent-Length: %u\r\n\r\n";

// Fungsi deklarasi
void startCameraServer();

void setup() {
  Serial.begin(115200);
  Serial.setDebugOutput(true);
  Serial.println();

  // Inisialisasi IO output
  pinMode(LED_HIJAU, OUTPUT);
  pinMode(LED_MERAH, OUTPUT);
  pinMode(BUZZER, OUTPUT);
  digitalWrite(LED_HIJAU, LOW);
  digitalWrite(LED_MERAH, LOW);
  digitalWrite(BUZZER, LOW);

  // Konfigurasi kamera
  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sccb_sda = SIOD_GPIO_NUM;
  config.pin_sccb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  config.frame_size = FRAMESIZE_CIF;
  config.pixel_format = PIXFORMAT_RGB565;
  config.grab_mode = CAMERA_GRAB_LATEST;
  config.fb_location = CAMERA_FB_IN_PSRAM;
  config.jpeg_quality = 12;
  config.fb_count = 1;

  // Inisialisasi kamera
  if (esp_camera_init(&config) != ESP_OK) {
    Serial.println("Camera init failed");
    return;
  }

  // Koneksi WiFi
  WiFi.begin(ssid, password);
  WiFi.setSleep(false);
  Serial.print("WiFi connecting");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi connected");

  // Mulai Web Server
  startCameraServer();

  Serial.print("Camera Ready! Access at http://");
  Serial.println(WiFi.localIP());
}

void loop() {
  delay(10000); // Loop kosong
}

void startCameraServer() {
  httpd_config_t config = HTTPD_DEFAULT_CONFIG();
  httpd_handle_t server = NULL;

  if (httpd_start(&server, &config) == ESP_OK) {

    // Halaman Utama
    httpd_uri_t index_uri = {
      .uri = "/",
      .method = HTTP_GET,
      .handler = [](httpd_req_t *req) {
        const char* html =
          "<!DOCTYPE html><html><head><title>ESP32-CAM</title></head><body>"
          "<h1>Streaming Kamera</h1><img src='/stream' width='400'/>"
          "</body></html>";
        httpd_resp_send(req, html, HTTPD_RESP_USE_STRLEN);
        return ESP_OK;
      },
      .user_ctx = NULL
    };
    httpd_register_uri_handler(server, &index_uri);

    // Stream Kamera
    httpd_uri_t stream_uri = {
      .uri = "/stream",
      .method = HTTP_GET,
      .handler = [](httpd_req_t *req) {
        camera_fb_t * fb = NULL;
        esp_err_t res = ESP_OK;
        size_t _jpg_buf_len;
        uint8_t * _jpg_buf;
        char * part_buf[64];

        res = httpd_resp_set_type(req, _STREAM_CONTENT_TYPE);
        if (res != ESP_OK) return res;

        while (true) {
          fb = esp_camera_fb_get();
          if (!fb) {
            Serial.println("Camera capture failed");
            return ESP_FAIL;
          }

          if (fb->format != PIXFORMAT_JPEG) {
            bool jpeg_converted = frame2jpg(fb, 80, &_jpg_buf, &_jpg_buf_len);
            if (!jpeg_converted) {
              Serial.println("JPEG compression failed");
              esp_camera_fb_return(fb);
              continue;
            }
          } else {
            _jpg_buf = fb->buf;
            _jpg_buf_len = fb->len;
          }

          res = httpd_resp_send_chunk(req, _STREAM_BOUNDARY, strlen(_STREAM_BOUNDARY));
          if (res == ESP_OK) {
            size_t hlen = snprintf((char *)part_buf, 64, _STREAM_PART, _jpg_buf_len);
            res = httpd_resp_send_chunk(req, (const char *)part_buf, hlen);
          }
          if (res == ESP_OK) {
            res = httpd_resp_send_chunk(req, (const char *)_jpg_buf, _jpg_buf_len);
          }

          if (fb->format != PIXFORMAT_JPEG) {
            free(_jpg_buf);
          }
          esp_camera_fb_return(fb);

          if (res != ESP_OK) break;
        }

        return res;
      },
      .user_ctx = NULL
    };
    httpd_register_uri_handler(server, &stream_uri);

    // Endpoint: APD Lengkap
    httpd_uri_t apd_lengkap_uri = {
      .uri = "/apd_lengkap",
      .method = HTTP_GET,
      .handler = [](httpd_req_t *req){
        digitalWrite(LED_HIJAU, HIGH);
        digitalWrite(LED_MERAH, LOW);
        digitalWrite(BUZZER, HIGH);
        delay(250);
        httpd_resp_send(req, "APD lengkap - LED hijau nyala", HTTPD_RESP_USE_STRLEN);
        return ESP_OK;
      },
      .user_ctx = NULL
    };
    httpd_register_uri_handler(server, &apd_lengkap_uri);

    // Endpoint: APD Tidak Lengkap
    httpd_uri_t apd_tidak_uri = {
      .uri = "/apd_tidak_lengkap",
      .method = HTTP_GET,
      .handler = [](httpd_req_t *req){
      digitalWrite(LED_HIJAU, LOW);

      for (int i = 0; i < 6; i++) {  // total 3 kali kedipan
        digitalWrite(LED_MERAH, HIGH);
        digitalWrite(BUZZER, HIGH);
        delay(250);
        digitalWrite(LED_MERAH, LOW);
        digitalWrite(BUZZER, LOW);
        delay(250);
      }

        httpd_resp_send(req, "APD tidak lengkap - LED merah & buzzer nyala", HTTPD_RESP_USE_STRLEN);
        return ESP_OK;
      },
      .user_ctx = NULL
    };
    httpd_register_uri_handler(server, &apd_tidak_uri);

    // Endpoint: Tidak Ada Objek
    httpd_uri_t kosong_uri = {
      .uri = "/kosong",
      .method = HTTP_GET,
      .handler = [](httpd_req_t *req){
        digitalWrite(LED_HIJAU, LOW);
        digitalWrite(LED_MERAH, LOW);
        digitalWrite(BUZZER, LOW);
        httpd_resp_send(req, "Tidak ada objek - Semua OFF", HTTPD_RESP_USE_STRLEN);
        return ESP_OK;
      },
      .user_ctx = NULL
    };
    httpd_register_uri_handler(server, &kosong_uri);
  }
}
