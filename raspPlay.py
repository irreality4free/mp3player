#! /usr/bin/env python

import datetime
import time
import pygame
import sys
import os
import select
import log_config
from log_config import trace
from log_config import log_error
from log_config import log_info

class Player():
    @trace
    def __init__(self):
        log_info('Starting player')
        self.workDir='/home/pi/mp3player'
        self.cmdDir='/home/pi/mp3player/CmdF/control.txt'
        self.cmdAnsw='/home/pi/mp3player/CmdF/answ.txt'
        self.sndDir='/home/pi/mp3player/files/'
        self.npFile='/home/pi/mp3player/CmdF/playlist.txt'
        self.stateFile = '/home/pi/mp3player/CmdF/nowstate.txt'
        self.Erase = False
        self.Break = False
        self.DictofFiles={}
        self.listFiles=[]
        self.repeat = False
        self.stateBool = False
        self.commands_dict={'set_volume':'set_volume','playFile':'playFile','stop':'stop', 'next':'next', 'prev':'prev', 'status':'status','repeate':'repeate'}
        numOfLines=0
        for x,line in enumerate(os.listdir(os.getcwd())):

                    if 'mp3' in line:
                        numOfLines+=1
                        self.DictofFiles[str(numOfLines)]=x
                        self.listFiles.append(x)
        
        
    @trace    
    def menu_unit(self,unitName, subunitsNum,):
        pass
    
            
    @trace    
    def playFile(self,name,timestamp,command):
        os.chdir(self.sndDir)
        print('current dir: ' +str(os.getcwd()))
        print('play file')
        numOfLines=0

        self.listFiles=[]
        for x,line in enumerate(os.listdir(self.sndDir)):

            if 'mp3' in line:
                numOfLines+=1

                self.listFiles.append(x)
                log_info('file found '+str(line))

        print('directory files:')
        print(os.listdir(self.sndDir))
                
                
        log_info('playing file ' + str(name))
        numInList=None

        for x,line in enumerate(os.listdir(self.sndDir)):
            if name in line:
                numInList = x
        for x,line in enumerate(self.listFiles):

            if line == numInList:

                if x<len(self.listFiles)-1:
                    nextFile = self.listFiles[x+1]
                else:
                    nextFile = self.listFiles[0]
                    
                if x>0:
                    prevFile = self.listFiles[x-1]
                else:
                    prevFile = self.listFiles[len(self.listFiles)-1]
                    
        print('Next file: ' + str(nextFile)+' '+ str(os.listdir(self.sndDir)[nextFile]))
        print('Prev file: ' + str(prevFile)+' '+ str(os.listdir(self.sndDir)[prevFile]))
        self.SaveNP(os.listdir(self.sndDir)[nextFile],os.listdir(self.sndDir)[prevFile])
                
 
                    
        pygame.init()
        pygame.mixer.init()
        
        print('loading... '+str(name))
        
        pygame.mixer.music.load(name)
        pygame.mixer.music.play()
        print('started playing...')
        self.printState(name)
        self.FileAddRez(str(timestamp)+';'+'1')
        self.SaveState(1)
        while pygame.mixer.music.get_busy():
            if self.stateBool:
                self.printState(name)
                time.sleep(1);

            log_info(str(pygame.mixer.music.get_pos()//1000)+ ' sec')
##            r,_,_=select.select([sys.stdin],[],[],1)
            f_com = self.FileCommands(self.cmdDir)
            
            

            if f_com !='none':
                print(f_com)
                f_com = f_com.split(';')
                if len(f_com) == 3:
                    print('ready for playback commands input')
                    
                    timestamp_pl = f_com[0]
                    command_pl = f_com[1]
                    param_pl = f_com[2]
                    print('timestamp: '+ timestamp_pl)
                    print('command: '+ command_pl)
                    if  command_pl == self.commands_dict['stop']:
                            print('stop')
                            self.FileAddCmd(str(timestamp_pl)+";"+str(command_pl))
                            
                            self.Break=True
                            self.repeat = False
                            log_info(' command - stop playback')
                            
                    
                        
                    elif command_pl == self.commands_dict['set_volume']:
                        self.FileAddCmd(str(timestamp_pl)+";"+str(command_pl))
                        
                        try:
                            pygame.mixer.music.set_volume(float(param_pl)/100)
                            print('set volume...'+str(param_pl/100))
                            self.FileAddRez(str(timestamp_pl)+";1")
                        except: 
                        
                            self.FileAddRez(str(timestamp_pl)+";0")
                                    
                    
                    elif  command_pl == self.commands_dict['next']:
                        self.FileAddCmd(str(timestamp_pl)+";"+str(command_pl))
                        self.playFile(str(os.listdir(self.sndDir)[nextFile]),timestamp_pl,command_pl)
                        log_info('play next file')
                        self.FileAddRez(str(timestamp_pl)+";1")
                        
                    elif command_pl == self.commands_dict['prev']:
                        self.FileAddCmd(str(timestamp_pl)+";"+str(command_pl))
                        self.playFile(str(os.listdir(self.sndDir)[prevFile]),timestamp_pl,command_pl)
                        log_info('play previous file')
                        self.FileAddRez(str(timestamp_pl)+";1")
                        
                    elif  command_pl == self.commands_dict['status']:
                        self.FileAddCmd(str(timestamp_pl)+";"+str(command_pl))
                        self.stateBool = not self.stateBool
                        log_info('status view changed')
                        self.FileAddRez(str(timestamp_pl)+";1")
                        
                    elif command == self.commands_dict['playFile']:
                        
                        try:
                                print(command)
                                self.playFile(param_pl,timestamp_pl,command_pl)
                                
                        except pygame.error:
                                print('wrong name')
                                self.FileAddRez(str(timestamp)+';'+'0')
                        
                    elif  command_pl == self.commands_dict['repeate']:
                        self.FileAddCmd(str(timestamp_pl)+";"+str(command_pl))
                        self.repeat = not self.repeat
                        self.FileAddRez(str(timestamp_pl)+";1")
                        
                            
                        print('\nrepeat - ' + str(self.repeat)+'\n')
                        log_info('repeat value changed')
                    else:

                        self.FileAddRez(str(timestamp_pl)+';0')
                        self.FileCommandsErase(self.cmdDir)
                else:
                    self.FileAddRez('wrong command')
                    self.FileCommandsErase(self.cmdDir)
                
            if self.Break:
                    self.stop()
                    self.FileAddRez(str(timestamp_pl)+";1")
                    self.Break=False
                    log_info('playback stopped')
           
                    
        print('end of file')
        log_info('end of file')
        self.SaveState(0)
        if self.repeat:
            self.playFile(name,'repeate file','1')
            
    @trace    
    def stop(self):
        pygame.mixer.music.stop()
    @trace    
    def minusDb(self):
        currentVol= pygame.mixer.music.get_volume()
        pygame.mixer.music.set_volume(currentVol-0.1)
        if pygame.mixer.music.get_volume()<0:
            pygame.mixer.music.set_volume(0)
        print(pygame.mixer.music.get_volume())
    @trace    
    def plusDb(self):
        currentVol= pygame.mixer.music.get_volume()
        pygame.mixer.music.set_volume(currentVol+0.1)
        if pygame.mixer.music.get_volume()<0:
            pygame.mixer.music.set_volume(0)
        print(pygame.mixer.music.get_volume())
        
    
               
    @trace    
    def printState(self,name):        
        print('playing...'+name)
        print(str(pygame.mixer.music.get_pos()//1000)+ ' sec')
        print('volume - '+str(pygame.mixer.music.get_volume()))
        print('repeat - '+str(self.repeat)+'\n')
        
    def FileCommands(self,file_name):
        if os.path.getsize(file_name) > 0:
            data = 'none'
            with open(file_name, 'r') as file:
                for string in file:
                    data = string

                
            with open(file_name, 'w') as file:
                pass
            return data
        else:
            return 'none'
    
    def FileCommandsErase(self,file_name):
        with open(file_name, 'w') as file:
            pass
        
    def FileAddCmd(self,cmd):
        with open(self.cmdAnsw, 'a') as file:
            file.write('\n'+str(cmd)+ ' ' +str(datetime.datetime.now()) )
            
    def FileAddRez(self, rez):
        with open(self.cmdAnsw, 'a') as file:
            file.write('\n'+str(rez) )
            
    def SaveNP(self,next,prev):
        with open(self.npFile, 'w') as file:
            file.write(str(next)+';'+str(prev))
        
    def SaveState(self,state):
        with open(self.stateFile, 'w') as file:
            if state == 1:
                file.write('playing')
            if state == 0:
                file.write('not playing')
        
            
        
    def Run(self):
        os.chdir(self.sndDir)
        print(os.getcwd())
        if self.Erase:
            self.FileCommandsErase(self.cmdAnsw)
        print('start')

        while(1):

            command = self.FileCommands(self.cmdDir)
            if command != 'none':
		print(command)
		com_list = command.split(';')
		if len(com_list) == 3:
                    timestamp = com_list[0]
                    command = com_list[1]
                    param = com_list[2]
                    self.FileAddCmd(str(timestamp)+';'+str(command))
                    if command == self.commands_dict['playFile']:
                        
                        try:
                                print(command)
                                self.playFile(param,timestamp,command)
                                
                        except pygame.error:
                                print('wrong name')
                                self.FileAddRez(str(timestamp)+';'+'0')
                    else:
                        print('wrong command')
                        self.FileCommandsErase(self.cmdDir)
                        self.FileAddRez(str(timestamp)+';'+'0')
                            
                else:
                    print('wrong command')
                    self.FileCommandsErase(self.cmdDir)
                    self.FileAddRez(str(timestamp)+';'+'0')
                
                
        
        
    
    
player = Player()
player.Run()
##player.playFile('test1.mp3')

