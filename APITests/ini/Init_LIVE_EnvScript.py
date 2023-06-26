'''
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
@author: moran.cohen

@name: Init_LIVE_EnvScript.py

 @desc : This script prepares new data to new env.
 Script input:BEenvID,ServerURL,PartnerAdminKS,
 Script output: ini file

TASKS:
1)
origin entry for nvq1: 0_13pp3oyp. Clipped entry for nvq1: 0_h3rbogmq
add audio flavors to CP 2121 (Audio-only ENG - (AAC) + Audio-only SPA - (AAC) )
create once imulive_Playlist_PrePostEntries_MultiCaptionAudio_PlaylistItem_* with the same video file as in nvq1
verifiy in nvd1 new created entries - they have "audio_only,alt_audio"
remove audio flavors from CP 2121


1)add delivery profile to partner config adminconsole
2)create DP_table
3)S3 files/PROD
4)push secret ini

for test_930_Simulive_Playlist_PrePostEntries_MultiCaptionAudio"
1.Add Captions
2.create new CP for multi-audio and use it

 %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
 '''
import os
import configparser
from KalturaClient import *
from KalturaClient.Plugins.Core import *

AdminKS = "MTgwNTAwNTE5MDNiYmQwZDc2M2VlMDZlOTI5Nzc4MjhkYjEzZWQ0Mnw2NjExOzY2MTE7MTY4NzE2ODYyNjsyOzE2ODcwODIyMjYuMTg4NDtMSVZFTkcxQG1haWxpbmF0b3IuY29tOyosZGlzYWJsZWVudGl0bGVtZW50Ozs"  # os.getenv('PartnerAdminKS')
ServerURL = "https://qa-apache-php7.dev.kaltura.com"  # os.getenv('ServerURL')
BEenvID = "nvq8"  # os.getenv('BEenvID')
sniffer_fitler_Before_Mp4flavorsUpload = "cloudfront"
sniffer_fitler_After_Mp4flavorsUpload = "cfvod-dev"
entries_data = [["AUTOMATION:SIMULIVEWithAC_vodId","http://qa-apache-php7.dev.kaltura.com/p/6611/sp/661100/playManifest/entryId/0_4aanpwol/format/download/protocol/http/flavorParamIds/0"]]
Simulive_AdminKS = "MTM4NzNjZDU0ZWM3ZTY5M2Y1ODIyZTcxNmNhNjcyMWE0MjJiZTc1OXw2ODE0OzY4MTQ7MTY4NzE2ODY1MDsyOzE2ODcwODIyNTAuMjg4NztMSVZFTkdfQVVUT01BVElPTjBfU0lNVUxJVkU5MDkyMV9AbWFpbGluYXRvci5jb207KixkaXNhYmxlZW50aXRsZW1lbnQ7Ow"
hybridcdn_AdminKS = "NWYzZjc5OTE3ZWMwNGY1ZDAyM2I1OGViMzBkNzMyNWM3MzllMjU2Znw5MDI1MTA1OzkwMjUxMDU7MTY4NzE2ODY3NTsyOzE2ODcwODIyNzUuMDgyMjtMSVZFTkdfSHlicmlkQ0ROX0F1dG9tYXRpb25AbWFpbGluYXRvci5jb207KixkaXNhYmxlZW50aXRsZW1lbnQ7Ow"


class InitCreator:

    def __init__(self):
        self.client = self._create_client()

    def _create_client(self):
        config = KalturaConfiguration()
        config.serviceUrl = ServerURL
        client = KalturaClient(config)
        client.setKs(AdminKS)
        return client

    def get_partner(self):
        filter = KalturaPartnerFilter()
        pager = KalturaFilterPager()
        result = self.client.partner.list(filter, pager)
        return result.objects[0]

    def set_default_partner_data(self,write_config):
        # Set partner data
        partner = self.get_partner()
        write_config.add_section("DefaultPartner")
        write_config.set("DefaultPartner", "partnerId", str(partner.id))
        write_config.set("DefaultPartner", "adminSecret", partner.adminSecret)

        '''
        write_config.set("DefaultPartner","ExistEntry",)
        write_config.set("DefaultPartner","reachProfileId",)
        write_config.set("DefaultPartner","catalogItemId",)
        write_config.set("DefaultPartner","access_control_id_DP_FOR_VODentry",)
        write_config.set("DefaultPartner","access_control_id_Default",)
        write_config.set("DefaultPartner","access_control_id_CFtokanization",)
        write_config.set("DefaultPartner","access_control_id_CFtokanization_Redirect",)
        write_config.set("DefaultPartner","access_control_id_lowlatency",)
        write_config.set("DefaultPartner","DP_table",)
        

        write_config.set("DefaultPartner","SIMULIVEWithAC_access_control_id",) #20327 of simulive playback
        write_config.set("DefaultPartner","SIMULIVEWithAC_conversionProfileID",) # default? 27011 Passthrough
        write_config.set("DefaultPartner","SIMULIVEWithAC_vodId",) #0_4aanpwol
        '''
    def set_env_data(self,write_config):
        write_config.add_section("Environment")
        write_config.set("Environment", "BE_ID", BEenvID)
        write_config.set("Environment", "ServerURL", ServerURL)

    def set_streamers_data(self,write_config):
        write_config.add_section("STREAMERS")
        write_config.set("STREAMERS", "LocalCheckpointKey", "CheckpointKey_Moran2.pem")
        write_config.set("STREAMERS", "remote_host_LiveNG_5", "10.101.0.254")
        write_config.set("STREAMERS", "remote_user_LiveNG_5", "ec2-user")
        write_config.set("STREAMERS", "remote_host_LiveNG_LiveCaption_4", "10.101.3.107")
        write_config.set("STREAMERS", "remote_user_LiveNG_LiveCaption_4", "ec2-user")
        write_config.set("STREAMERS", "remote_host_LIVENG_Recording", "10.101.100.235")
        write_config.set("STREAMERS", "remote_user_LIVENG_Recording", "ec2-user")
        write_config.set("STREAMERS", "remote_host_LIVENG_Recording", "10.101.1.111")
        write_config.set("STREAMERS", "remote_user_LIVENG_Recording", "ec2-user")
        write_config.set("STREAMERS", "remote_host_LIVENG_Recording", "10.101.101.216")
        write_config.set("STREAMERS", "remote_user_LIVENG_Recording", "ec2-user")
        write_config.set("STREAMERS", "remote_host_LIVENG_Kubernetes", "10.101.2.133")
        write_config.set("STREAMERS", "remote_user_LIVENG_Kubernetes", "ec2-user")

    def set_recording_data(self,write_config):
        write_config.add_section("RECORDING")
        write_config.set("RECORDING", "sniffer_fitler_Before_Mp4flavorsUpload",sniffer_fitler_Before_Mp4flavorsUpload)
        write_config.set("RECORDING", "sniffer_fitler_After_Mp4flavorsUpload",sniffer_fitler_After_Mp4flavorsUpload)

    def media_add(self,entry_name="0"):
        entry = KalturaMediaEntry()
        entry.mediaType = KalturaMediaType.VIDEO
        entry.name = entry_name
        result = self.client.media.add(entry)
        return result

    def media_updateContent_by_resourceurl(self, entry_id, resource_url):
        resource = KalturaUrlResource()
        resource.url = resource_url
        conversion_profile_id = 0
        advanced_options = KalturaEntryReplacementOptions()
        result = self.client.media.updateContent(entry_id, resource, conversion_profile_id, advanced_options)
        return result

    def create_mediaEntries_By_resourceurl(self, entries_data):
        try:
            entry=self.media_add(entries_data[0][0])
            self.media_updateContent_by_resourceurl(entry.id,entries_data[0][1])
            return True
        except Exception as e:
            print(e)
            return False

    def create_mediaEntry_By_resourceurl(self, entry_name,entry_resourceurl):
        try:
            entry=self.media_add(entry_name)
            self.media_updateContent_by_resourceurl(entry.id,entry_resourceurl)
            return entry.id
        except Exception as e:
            print(e)
            return False

    def getDefault_conversionProfile_live(self):
        k_type = KalturaConversionProfileType.LIVE_STREAM
        result = self.client.conversionProfile.getDefault(k_type)
        return result.id

    def set_simulive_data(self,write_config):
        self.client.setKs(Simulive_AdminKS)
        partner = self.get_partner()
        write_config.add_section("SIMULIVE")
        write_config.set("SIMULIVE", "partnerId", str(partner.id))
        write_config.set("SIMULIVE", "adminsecret",partner.adminSecret)
        write_config.set("SIMULIVE", "SIMULIVE_conversionProfileID",str(self.getDefault_conversionProfile_live()))
        write_config.set("SIMULIVE", "SIMULIVE_vodId",self.create_mediaEntry_By_resourceurl("SIMULIVE_vodId","http://cdnapi.kaltura.com/p/4281553/sp/428155300/playManifest/entryId/1_7tn8q9y5/format/download/protocol/http/flavorParamIds/0"))
        '''                 
        write_config.set("SIMULIVE", "SIMULIVE_kwebcastProfileId,)#optional
        write_config.set("SIMULIVE", "SIMULIVE_MainEntryId,)
        write_config.set("SIMULIVE", "SIMULIVE_preStartEntryId,)
        write_config.set("SIMULIVE", "SIMULIVE_postEndEntryId,)
        write_config.set("SIMULIVE", "SimuliveToLivePRE_MainEntryId,)
        write_config.set("SIMULIVE", "SimuliveToLivePRE_preStartEntryId,)
        write_config.set("SIMULIVE", "SimuliveToLivePRE_postEndEntryId,)
        write_config.set("SIMULIVE", "SimuliveToLivePOST_MainEntryId_Ron2min,)
        write_config.set("SIMULIVE", "SimuliveToLivePOST_preStartEntryId_Ron1min,)
        write_config.set("SIMULIVE", "SimuliveToLivePOST_postEndEntryId_Dual10min,)
        write_config.set("SIMULIVE", "SimuliveToLiveMAIN_isContentInterruptibleFalseDefault_MainEntryId_Daul5min,)
        write_config.set("SIMULIVE", "SimuliveToLiveMAIN_isContentInterruptibleFalseDefault_preStartEntryId_Ron1min,)
        write_config.set("SIMULIVE", "SimuliveToLiveMAIN_isContentInterruptibleFalseDefault_postEndEntryId_Dual10min,)
        write_config.set("SIMULIVE", "SimuliveToLiveMAIN_isContentInterruptibleTrue_MainEntryId_Daul10min,)
        write_config.set("SIMULIVE", "SimuliveToLiveMAIN_isContentInterruptibleTrue_preStartEntryId_Ron1min,)
        write_config.set("SIMULIVE", "SimuliveToLiveMAIN_isContentInterruptibleTrue_postEndEntryId_Dual5min,)
        write_config.set("SIMULIVE", "SimuliveEventShorterThanSourcesDuration_MainEntryId_Ron5min,)
        write_config.set("SIMULIVE", "SimuliveEventShorterThanSourcesDuration_preStartEntryId_Ron1min,)
        write_config.set("SIMULIVE", "SimuliveEventShorterThanSourcesDuration_postEndEntryId_Prince2min,)
        write_config.set("SIMULIVE", "Simulive_Playlist_BasicFlow_PlaylistItem1_Ron1min,)
        write_config.set("SIMULIVE", "Simulive_Playlist_BasicFlow_PlaylistItem2_Ron3min,)
        write_config.set("SIMULIVE", "Simulive_Playlist_BasicFlow_PlaylistItem3_Ron2min,)
        write_config.set("SIMULIVE", "Simulive_Playlist_PrePostEntries_MultiCaptionAudio_preStartEntryId_Ron1min,)
        write_config.set("SIMULIVE", "Simulive_Playlist_PrePostEntries_MultiCaptionAudio_PlaylistItem1_Clip1Sintel4min,)
        write_config.set("SIMULIVE", "Simulive_Playlist_PrePostEntries_MultiCaptionAudio_PlaylistItem2_Clip2Sintel4min,)
        write_config.set("SIMULIVE", "Simulive_Playlist_PrePostEntries_MultiCaptionAudio_postEndEntryId_Ron2min,)
        write_config.set("SIMULIVE", "Simulive_Playlist_ToLIVE_isContentInterruptibleTrue_PlaylistItem1_Dual3min,)
        write_config.set("SIMULIVE", "Simulive_Playlist_ToLIVE_isContentInterruptibleTrue_PlaylistItem2_Dual3min,)
        write_config.set("SIMULIVE", "Simulive_Playlist_ToLIVE_isContentInterruptibleTrue_PlaylistItem3_Dual4min,)
        '''

    def set_hybridcdn_data(self, write_config):
        self.client.setKs(hybridcdn_AdminKS)
        partner = self.get_partner()
        write_config.add_section("HYBRIDCDN")
        write_config.set("HYBRIDCDN", "partnerId", str(partner.id))
        write_config.set("HYBRIDCDN", "adminsecret", partner.adminSecret)

    def init_env_for_live(self):
        try:
            # Write INI file
            write_config = configparser.ConfigParser()
            self.set_env_data(write_config)
            self.set_default_partner_data(write_config)
            self.set_streamers_data(write_config)
            self.set_recording_data(write_config)
            self.set_simulive_data(write_config)
            self.set_hybridcdn_data(write_config)
            file_name = "LIVE_" + BEenvID + ".ini"
            with open(file_name, 'w') as cfgfile:
                write_config.write(cfgfile)

            print ("Created filie ini = " + file_name)

        except Exception as Exp:
            print(Exp)
            pass


if __name__ == '__main__':
    ic = InitCreator()
    ic.init_env_for_live()


