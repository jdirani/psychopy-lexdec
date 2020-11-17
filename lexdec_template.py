from psychopy import visual, core, event, data
import csv, random, pyxid, time, os

experiment_dir = '/Users/julien/Desktop/psychopy_templates/lexdec'
os.chdir(experiment_dir)

'''....................Stimtracker...........................................'''
# This sets the Cedrus StimTracker box in order to send the triggers

class NullStimtracker(object):
    def activate_line(self, bitmask=None):
        pass

# Looks for stimtracker hardware, if not found: sends a warning
def get_stimtracker(trigger_duration=5):
    for dev in pyxid.get_xid_devices():
        if dev.is_stimtracker():
            dev.set_pulse_duration(trigger_duration)
            return dev
    print "STIMTRACKER NOT FOUND!"
    decision=raw_input('Continue anyway? [y/n]: ')
    if decision=='y':
        return NullStimtracker()
    else:
        core.quit()

triggerBox = get_stimtracker() #run the function above, saving stimtracker as triggerBox



'''.................... Experiment and Participant info ......................'''
expInfo={}
expInfo['Participant']= raw_input('Participant: ')
expInfo['Run']=raw_input('Prac-Expt: ')



'''.................... Create experiment objects ..........................'''

win = visual.Window(monitor="testMonitor", units="pix", fullscr=True, colorSpace='rgb255', color=[127,127,127])
word = visual.TextStim(win,text='', font='Courier New', wrapWidth=500, alignHoriz='center', height=40, color=(-1,-1,-1))
fixation = visual.TextStim(win, text='+', height=40, color=(-1,-1,-1))
instructions = visual.TextStim(win,text='', font='Courier New', wrapWidth=800, alignHoriz='center', height=30, color=(-1,-1,-1))
photodiode = visual.Rect(win, width=90, height=90, pos=[510,360], fillColor=[255,255,255], fillColorSpace='rgb255')
rtClock = core.Clock()

win.mouseVisible = False #This hides the mouse.



'''........................... Functions ....................................'''
# Presenting instructions to the screen.
# When using this, edit "text=''" to contain your instructions
def present_instructions(text=''):
    instructions.setText(text)
    instructions.draw()
    win.flip()
    return event.waitKeys(keyList=['1']) #This waits for "1" to continue, edit if need other buttons


def present_fix():
    for frame in range (36): #600ms, draws fixation for 300ms then blank for 300ms
        if frame <= 18:
            fixation.draw()
        win.flip()


# Presents a word that stays on screen until response
def present_word(text='', trigger=None, photoDiode=True):
    word.setText(text)
    if trigger:
        win.callOnFlip(triggerBox.activate_line, bitmask=int(trigger))
    win.callOnFlip(rtClock.reset)
    word.draw()
    if photoDiode:
        photodiode.draw()
    win.flip()
    return event.waitKeys(keyList=['1','2', 'q'], timeStamped=rtClock)


def make_blocks(stim, n):
    # Creates n blocks from stim. nb stim must be dividable by n.
    # no back to back repeats by default, because unique targets in each block

    # ADD BACK TO BACK REPEAT CHECK IN TEMPLATE.
    out = []
    for j in range(0, len(stim), len(stim)/n):
            out.append(stim[j:j+len(stim)/n])
    for i in out:
        random.shuffle(i)
    return out



'''.......................Experiment starts here..............................'''

##---------------------------Practice-------------------------------------##
if expInfo['Run'] == 'Prac':

    with open('lexdec_practice.csv') as f:
        trials_practice = [i for i in csv.DictReader(f)]
    random.shuffle(trials_practice)

    present_instructions('You will start the practice now.')

    for trial in trials_practice:
        present_fix()
        resp = present_word(text=trial['target']) #present target
        win.flip()
        if resp[0][0] == trial['correct_ans']:
            present_instructions('Correct! Press to continue.')
        elif resp[0][0] == 'q':
            win.close()
            core.quit()
        else:
            present_instructions('Wrong! Press to continue')

    present_instructions('The practice is over.')





# Fix coming part



##-------------------------Experiment------------------------------------##
elif expInfo['Run'] == 'Expt':

    #Importing stimuli
    with open('lexdec_stim.csv') as f:
        trials = [i for i in csv.DictReader(f)]

    exp = data.ExperimentHandler(dataFileName='%s_logfile' %expInfo['Participant'], autoLog=False, savePickle=False)

    present_instructions('Lexical decision task: index (2) for words, middle finger (1) for non words.')

    #randomize and block the trials
    random.shuffle(trials)
    blocks = make_blocks(trials,4) #4 blocks in this case
    trialnum = 0
    blocknum = 0

    for block in blocks:
        if blocknum > 0:
            prompt = 'You have completed block #'+str(blocknum)+". Take a break, then press 1 when you are ready to continue."
            present_instructions(prompt)

        for trial in block:
            present_fix()
            resp = present_word(text=trial['target'])
            win.flip()
            if resp[0][0] == 'q':
                win.close()
                core.quit()
            core.wait(random.gauss(1.0,0.167)) #isi
            trialnum += 1


            exp.addData('participant', expInfo['Participant'])
            exp.addData('trialnum', trialnum)
            exp.addData('target', trial['target'])
            exp.addData('target_type', trial['target_type'])
            exp.addData('trigger', trial['trigger'])
            exp.addData('response', resp[0][0])
            exp.addData('RT', resp[0][1])
            if resp[0][0] == trial['correct_ans']:
                exp.addData('hit', 1)
            else:
                exp.addData('hit', 0)
            exp.nextEntry()

        blocknum += 1

    present_instructions('The experiment is over. Thank you.')

win.close()
core.quit()
