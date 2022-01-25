create user voiceauth with password 'voiceauth';
create database voiceauth owner voiceauth;

\c voiceauth;
set role voiceauth;

create table voiceauth (
    id bigserial primary key,
    created timestamp with time zone default now(),
    dst varchar(16) not null default '',
    updated timestamp with time zone default null,
    src varchar(16) not null default '',
    hangup_cause int not null default 0
);

create index on voiceauth (created);
create index on voiceauth (dst);
create index on voiceauth (updated);



