create table if not exists users (
  email character varying primary key not null,
  password character varying not null,
  name character varying not null
);
create table if not exists messages (
  message_id uuid primary key not null default gen_random_uuid(),
  content character varying not null,
  send_at timestamp not null,
  email character varying not null references users,
  channel_id uuid not null references channels
);
create table if not exists channels (
  channel_id uuid primary key not null default gen_random_uuid(),
  name character varying not null
);
create table if not exists channels_members (
  channel_id uuid not null references channels,
  email character varying not null references users,
  primary key (channel_id, email)
);
