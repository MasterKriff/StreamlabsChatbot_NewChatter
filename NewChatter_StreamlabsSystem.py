#!/usr/bin/python
# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
"""Play a sound if there is a new chatter in the stream."""

#---------------------------------------
# Libraries and references
#---------------------------------------
import codecs
import json
import os
import re
import ctypes
import winsound

#---------------------------------------
# [Required] Script information
#---------------------------------------
ScriptName = "New Chatter Notification"
Website = ""
Creator = "MasterKriff"
Version = "1.0"
Description = "Play a sound if there is a new chatter in the stream."

#---------------------------------------
# Versions
#---------------------------------------
""" Releases (open README.txt for full release notes)
1.0 - Initial Release
"""

#---------------------------------------
# Variables
#---------------------------------------
SettingsFile = os.path.join(os.path.dirname(__file__), "settings.json")
UserListFile = os.path.join(os.path.dirname(__file__), "userlist.txt")
MessageBox = ctypes.windll.user32.MessageBoxW

#---------------------------------------
# Classes
#---------------------------------------
class Settings:
    """" Loads settings from file if file is found if not uses default values"""

    # The 'default' variable names need to match UI_Config
    def __init__(self, settingsFile=None):
        if settingsFile and os.path.isfile(settingsFile):
            with codecs.open(settingsFile, encoding='utf-8-sig', mode='r') as f:
                self.__dict__ = json.load(f, encoding='utf-8-sig')
        else: #set variables if no custom settings file is found
            self.NewChatterSoundLocation = os.path.join(os.path.dirname(__file__), "newchatter.mp3")
            self.PlayNewChatterSound = False
            self.Volume = 50
            self.NewChatterMessage = "Welcome to the stream {0}! <3"
            self.SendNewChatterMessage = False

    # Reload settings on save through UI
    def Reload(self, data):
        """Reload settings on save through UI"""
        self.__dict__ = json.loads(data, encoding='utf-8-sig')

    def Save(self, settingsfile):
        """ Save settings contained within to .json and .js settings files. """
        try:
            with codecs.open(settingsfile, encoding="utf-8-sig", mode="w+") as f:
                json.dump(self.__dict__, f, encoding="utf-8", ensure_ascii=False)
            with codecs.open(settingsfile.replace("json", "js"), encoding="utf-8-sig", mode="w+") as f:
                f.write("var settings = {0};".format(json.dumps(self.__dict__, encoding='utf-8', ensure_ascii=False)))
        except ValueError:
            Parent.Log(ScriptName, "Failed to save settings to file.")

#---------------------------------------
# [OPTIONAL] Settings functions
#---------------------------------------
def BtnResetDefaults():
    """Set default settings function"""
    winsound.MessageBeep()
    MB_YES = 6

    returnValue = MessageBox(0, u"You are about to reset the settings, "
                                "are you sure you want to contine?"
                             , u"Reset settings file?", 4)

    if returnValue == MB_YES:
        MySettings = Settings()
        MySettings.Save(SettingsFile)
        returnValue = MessageBox(0, u"Settings successfully restored to default values"
                                 , u"Reset complete!", 0)

def BtnTestSound():
    """Test sound"""
    PlayNewChatterSound()

def BtnResetUserList():
    """Resets the user list file"""
    ResetUserListFile()
    MessageBox(0, u"The user list for new chatters has been reset."
                            , u"User list reset", 0)

def ReloadSettings(jsondata):
    """Reload settings on Save"""
    global MySettings
    MySettings.Reload(jsondata)
    
#---------------------------------------
# Base Functions
#---------------------------------------
def ResetUserListFile():
    """Resets the user list file"""
    with open(UserListFile, "w") as f:
        f.write("")

def IsUsernameInList(username):
    """Returns true if user is in the user list file"""
    with open(UserListFile, "r") as f:
        for line in f:
            if line.strip() == username:
                return True
    return False

def AddUserToList(username):
    """Add username to the user list file"""
    with open(UserListFile, "a") as f:
        f.write(username + "\n")

def SendChatMessage(message):
    """Required SendChatMessage function"""
    Parent.SendStreamMessage(message)

def PlayNewChatterSound():
    """Plays a sound when a new chatter joins the stream"""
    if os.path.isfile(MySettings.NewChatterSoundLocation):
        Parent.PlaySound(MySettings.NewChatterSoundLocation, MySettings.Volume*0.01)
    else:
        winsound.MessageBeep()

#---------------------------------------
# [Required] functions
#---------------------------------------
def Init():
    """data on Load, required function"""
    global MySettings
    MySettings = Settings(SettingsFile)
    ResetUserListFile()

def Execute(data):
    """Required Execute data function"""
    streamerName = Parent.GetChannelName()
    userName = data.UserName

    if userName == streamerName or IsUsernameInList(userName):
        return

    if MySettings.NewChatterSoundLocation and MySettings.PlayNewChatterSound:
        PlayNewChatterSound()

    if MySettings.NewChatterMessage and MySettings.SendNewChatterMessage:
        msg = MySettings.NewChatterMessage.format(userName)
        SendChatMessage(msg)

    AddUserToList(userName)

def Tick():
    """Required tick function"""