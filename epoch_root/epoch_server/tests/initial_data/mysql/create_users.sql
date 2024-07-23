CREATE USER `app_user`@`%` IDENTIFIED WITH 'caching_sha2_password' AS '$A$005$s9TTKEA3f+]#LOEbqChFl8omOh1z7ftZ1msiH4IzGwc7P3hEHAloSRsp4' REQUIRE NONE PASSWORD EXPIRE DEFAULT ACCOUNT UNLOCK PASSWORD HISTORY DEFAULT PASSWORD REUSE INTERVAL DEFAULT PASSWORD REQUIRE CURRENT DEFAULT;
GRANT USAGE ON *.* TO `app_user`@`%`;
GRANT ALL PRIVILEGES ON `epoch`.* TO `app_user`@`%`;