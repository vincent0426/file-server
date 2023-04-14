CREATE TABLE "users" (
  "id" uuid UNIQUE PRIMARY KEY NOT NULL,
  "username" varchar UNIQUE NOT NULL,
  "password" varchar NOT NULL,
  "pub_key" text UNIQUE NOT NULL
);

CREATE TABLE "files" (
  "id" uuid UNIQUE PRIMARY KEY NOT NULL,
  "content" bytea
);

CREATE TABLE "transactions" (
  "id" uuid UNIQUE PRIMARY KEY NOT NULL,
  "file_id" uuid,
  "enc_sym" bytea,
  "from" uuid,
  "to" uuid
);

ALTER TABLE "transactions" ADD FOREIGN KEY ("file_id") REFERENCES "files" ("id");

ALTER TABLE "transactions" ADD FOREIGN KEY ("from") REFERENCES "users" ("id");

ALTER TABLE "transactions" ADD FOREIGN KEY ("to") REFERENCES "users" ("id");
