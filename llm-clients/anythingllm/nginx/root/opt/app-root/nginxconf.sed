# Change port
/listen/s%80%8888 default_server%

# One worker only
/worker_processes/s%auto%1%

s/^user *nginx;//
s%/etc/nginx/conf.d/%/opt/app-root/etc/nginx.d/%
s%/etc/nginx/default.d/%/opt/app-root/etc/nginx.default.d/%
s%/usr/share/nginx/html%/opt/app-root/src%

# See: https://github.com/sclorg/nginx-container/pull/69
/error_page/d
/40x.html/,+1d
/50x.html/,+1d

# Addition for anythingllm Server
/server_name/s%server_name  _%server_name  ${BASE_URL}%
