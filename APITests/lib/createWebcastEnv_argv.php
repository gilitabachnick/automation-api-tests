<?php
require_once(dirname(__FILE__) . '/php5/KalturaClient.php');


//$config = parse_ini_file('config.ini',true);
$configFile = $argv[3];
$config = parse_ini_file($configFile,true);
$env = 'env';

$partnerID = $argv[5];//$config[$env]['partnerID'] ;
$adminSecret = $argv[6];//$config[$env]['adminSecret'];
$serviceUrl = $argv[7];//$config[$env]['serviceUrl'];
$conversionProfileID = $argv[8];//$config[$env]['transcodingProfile'];
$kwebcastProfileId = $argv[9];//$config[$env]['entryMetadataProfileId'];
$eventsProfileId = $argv[10];//$config[$env]['eventsProfileId'];
$isSimulive = $config[$env]['isSimulive'];
$vodId = $argv[11];//$config[$env]['vodId'];
//$sessionStart = $config[$env]['sessionStart'];
//$sessionEnd = $config[$env]['sessionEnd'];
$sessionStart = $argv[1];
$sessionEnd = $argv[2];
$timeZone = $config[$env]['timeZone'];
//$sessionTitle = $config[$env]['sessionTitle'];
$sessionTitle = $argv[4];
$groupName = $config[$env]['groupName'];
$manualLiveHlsUrl = $config[$env]['manualLiveHlsUrl'];
$manualLiveBackupHlsUrl = $config[$env]['manualLiveBackupHlsUrl'];
$isEmbargo = $config[$env]['isEmbargo'];
$userId = $config[$env]['userId'];

$config = new KalturaConfiguration ( $partnerID );
$config->serviceUrl = $serviceUrl;
$client = new KalturaClient ( $config );
$client->setPartnerId($partnerID);

//get the partner's ks with the admin secret
$ks = $client->session->start ( $adminSecret, $userId, KalturaSessionType::ADMIN, $partnerID, null, 'disableentitlement' );
$client->setKs($ks);

// TODO before we create new VOD/live first check if there is already one exists using the reference ID. If exists, update it.
if($isSimulive){
	$vodEntry = new KalturaMediaEntry();
	$vodEntry->mediaType = KalturaMediaType::VIDEO;
	$vodEntry->staname = $sessionTitle;
	$vodEntry->entitledUsersEdit = $groupName;
	$vodEntry->entitledUsersPublish = $groupName;
	$vodEntry->entitledUsersView = $groupName;
	$vodEntry->adminTags = $isSimulive ? 'simulive' : 'live';
	// TODO set session tags, description, reference ID, custom data
	if ($vodId == '') {
		$vodDraftEntry = $client->media->add($vodEntry);
		$vodId = $vodDraftEntry->id;
	}
}
if($isSimulive){
//TODO - add vodDraft to 'Simulive Source VODs' category (not under KMS). Not to a channel (Track)
}
else{
//TODO - add vodDraft to 'Live VOD Sessions' category (not under KMS). Not to a channel (Track)
}

// TODO the lines below should be repeated (creation of live entry and LiveStreamScheduleEvent) for each scheduling of the session according to CVENT sessionTime values

$entry = new KalturaLiveStreamEntry();
$entry->name = $sessionTitle;
$entry->type = KalturaEntryType::LIVE_STREAM;
$entry->mediaType = KalturaMediaType::LIVE_STREAM_FLASH;
//$entry->dvrStatus = KalturaDVRStatus::ENABLED;
$entry->recordStatus = KalturaRecordStatus::DISABLED;
//$entry->dvrWindow = 60;
$entry->conversionProfileId = $conversionProfileID;
$entry->adminTags = 'kms-webcast-event';
$entry->explicitLive = KalturaNullableBoolean::FALSE_VALUE;
$recordingOptions = new KalturaLiveEntryRecordingOptions();
$recordingOptions->shouldCopyEntitlement = KalturaNullableBoolean::TRUE_VALUE;
$recordingOptions->shouldMakeHidden = true;
$entry->recordingOptions = $recordingOptions;
$entry->userId = $groupName;
$entry->entitledUsersPublish = $groupName;
$entry->entitledUsersView = $groupName;
$entry->entitledUsersEdit = "WebcastingAdmin,$groupName";
if($isEmbargo){
    $entry->startDate = 1609459200; // 1.1.2021
}

$liveConfig = array();
if(!$isSimulive){
    $liveStreamConfigHls = new KalturaLiveStreamConfiguration();
    $liveStreamConfigHls->protocol = KalturaPlaybackProtocol::APPLE_HTTP;
// for starter - this will be a dummy URL. we will change this to the actual stream.
    $liveStreamConfigHls->url = $manualLiveHlsUrl; // need to get more info from Yair
    $liveStreamConfigHls->backupUrl = $manualLiveBackupHlsUrl;
    $liveConfig[] = $liveStreamConfigHls;
// without setting HDS KMS won't allow editing scheduling https://github.com/kaltura/mediaspace/blob/release/modulesCustom/core/kwebcast/models/Kwebcast.php#L884
    $liveStreamConfigHds = new KalturaLiveStreamConfiguration();
    $liveStreamConfigHds->protocol = KalturaPlaybackProtocol::HDS;
    $liveStreamConfigHds->url = "http://cdnapi.kaltura.com/p/551701/sp/55170100/playManifest/entryId/1_dijrhmu1/protocol/http/format/hds/a.f4m"; // need to get more info from Yair
    $liveConfig[] = $liveStreamConfigHds;
    $entry->liveStreamConfigurations = $liveConfig;
}

$sourceType = $isSimulive ? KalturaSourceType::LIVE_STREAM: KalturaSourceType::MANUAL_LIVE_STREAM;
// TODO set session tags, description, reference ID, channel (Track) , custom data (same as on the VOD)
$newEntry = $client->liveStream->add($entry, $sourceType);

$xml='<metadata>
    <SlidesDocEntryId></SlidesDocEntryId>
	<IsKwebcastEntry>1</IsKwebcastEntry>
</metadata>';
$metadataPlugin = KalturaMetadataClientPlugin::get($client);
$metadataPlugin->metadata->add($kwebcastProfileId,KalturaMetadataObjectType::ENTRY,$newEntry->id,$xml);

// KMS relies on this custom metadata as well, not just scheduledEvent
$xml = "<?xml version='1.0'?>
<metadata>
	<StartTime>$sessionStart</StartTime>
	<EndTime>$sessionEnd</EndTime>
	<Timezone>$timeZone</Timezone>
</metadata>";
$metadataPlugin->metadata->add($eventsProfileId,KalturaMetadataObjectType::ENTRY,$newEntry->id,$xml);

$ks = $client->session->start ( $adminSecret, 'kmsAdminServiceUser', KalturaSessionType::ADMIN, $partnerID, null, 'disableentitlement' );
$client->setKs($ks);
$scheduledEvent = new KalturaLiveStreamScheduleEvent();
$scheduledEvent->templateEntryId = $newEntry->id; // live entry ID

if($isSimulive)
{
    $scheduledEvent->sourceEntryId = $vodId;
}
//$scheduledEvent->preStartTime = $isSimulive ? 600 : 1800;
//$scheduledEvent->postEndTime = $isSimulive ? 300 : 600;


$scheduledEvent->startDate = $sessionStart; // the session start time
$scheduledEvent->endDate = $sessionEnd; // the session end time
$scheduledEvent->recurrenceType = KalturaScheduleEventRecurrenceType::NONE;
$scheduledEvent->summary = $sessionTitle;
$scheduledEvent->tags = $isSimulive ? 'simulive' : 'manual';
$scheduledEvent->organizer = 'adminGroup'; // can we set a group?
$schedulePlugin = KalturaScheduleClientPlugin::get($client);
$schedulePlugin->scheduleEvent->add($scheduledEvent);

echo $newEntry->id.PHP_EOL;