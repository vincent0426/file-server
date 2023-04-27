CREATE TABLE "users" (
  "id" uuid UNIQUE PRIMARY KEY NOT NULL,
  "username" varchar UNIQUE NOT NULL,
  "password" varchar NOT NULL,
  "pub_key" text NOT NULL
);

CREATE TABLE "transactions" (
  "id" uuid UNIQUE PRIMARY KEY NOT NULL,
  "file_id" uuid,
  "filename" varchar,
  "from_uid" uuid,
  "to_uid" uuid
);

ALTER TABLE "transactions" ADD FOREIGN KEY ("from_uid") REFERENCES "users" ("id");

ALTER TABLE "transactions" ADD FOREIGN KEY ("to_uid") REFERENCES "users" ("id");
