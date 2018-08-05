
clear-table:
	bq rm simresults.tracks
	bq mk --schema schema.json simresults.tracks

delete-all:
	bq update 'delete from simresults.tracks where true'

create-topic:
	gcloud pubsub topics create sim-results

publish:
	go run ./publish/*

summary:
	bq query 'select scenario, sum(split) as split, sum(spurious) as spurious from simresults.tracks group by scenario order by scenario'