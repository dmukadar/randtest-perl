CREATE TABLE cdr (
    acctSessionId char(64) primary key,
    callingStationId char(32),
    calledStationId char(32),
    setupTime datetime,
    connectTime datetime,
    disconnectTime datetime
) engine=InnoDB default charset=UTF8;