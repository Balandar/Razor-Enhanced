#------Vars
from datetime import datetime
# This is a combination of scripts from various sources for training skills.
################################
# Arrange these in the order that you would like to train the skill.  Remove any if you do not want to train them.
# Set skill to locked or down in game to skip/exclude from training if skill is in "order" below (such as spirit speak)
# Double check you are not at your skill cap or have skills turned down to avoid infinite recursion on some skill trainings.
# Train Chivalry, Magery, and Necro to at least 30 from a NPC if planning to train.. Also, use a 100% reagent reduction outfit
# To train healing, have bandages on person and a magic item that gives a strength bonus. Ignore the system error "move" messages.
# To train hiding, go to a remote location with few people around (top of rune library or your house)
# To train anatomy, use a second account (also macroing this script to train that avatar) and target the other account avatar
# To train vet, use a second account with a high hitpoint tamed creature that is set to "all stay". Add as friend to creature or same guild for attacking/damage.
order = ["vet","animallore"]

# possible skills to choose from, move/copy these to the 'order' array above.
freeskills = ["taste","picking","removetrap","taste","spirit","camp","hide","arms","item","detect","tracking","spellweaving","magery","healing","necro","evalint"]
others = ["spellweaving","necro","magery","chivalry","anatomy","healing","evalint","beg","vet","animallore"]

# using picks in your backpack?  Script cannot detect if picks outside of backpack are missing
useOwnPicks = True
longPause = 10500
shortPause = 1200


#----------
Player.HeadMessage(77, "!!!Starting!!!");

def skillStatus(skillName):
    skillStatusValue = Player.GetSkillStatus(skillName)
    return skillStatusValue

mainpack = Mobiles.FindBySerial( Player.Serial ).Backpack



if "healing" in order and skillStatus("healing") == 0:
    Player.HeadMessage(77, "!!! Target Str Armor !!!");
    hitPointArmor = Target.PromptTarget("Target your armor with stregth bonus (healing train)")

if ("anatomy" in order and skillStatus("anatomy") == 0) or ("evalint" in order and skillStatus("Evaluating Intelligence") == 0) :
    Player.HeadMessage(77, "!!! Target Anatomy or Eval Int Mob !!!");
    anatomyTarget = Target.PromptTarget( 'Select mob to train on (recommended to use a pet)' )
    Mobiles.Message( anatomyTarget, 52, 'Selected for anatomy or eval int training' )

if ("beg" in order and skillStatus("begging") == 0) :
    Player.HeadMessage(77, "!!! Target Begging Mob !!!");
    beggingTarget = Target.PromptTarget( 'Select mob to train on' )
    Mobiles.Message( beggingTarget, 52, 'Selected for Begging training' )

if (("vet" in order and skillStatus("veterinary") == 0) or ("animallore" in order and skillStatus("Animal Lore") == 0)) :
    Player.HeadMessage(77, "!!! Target veterinary or Animal Lore Mob !!!");
    veterinaryTarget = Target.PromptTarget( 'Select mob to train on' )
    Mobiles.Message( veterinaryTarget, 52, 'Selected for veterinary or animal lore training' )

if "camp" in order and skillStatus("camping") == 0:
    kindlingId = 0x0DE1
    kindling = Items.FindByID(int(kindlingId),0,mainpack.Serial,-1,False)

if ("item" in order and skillStatus("Item ID") == 0) or ("arms" in order and skillStatus("Arms Lore") == 0):
    Player.HeadMessage(77, "!!! Target Armor or Weapon !!!");
    weaponId = Target.PromptTarget("Target a weapon or armor (arms lore or item id)")

if "taste" in order and skillStatus("Taste ID") == 0:
    Player.HeadMessage(77, "!!! Target Food !!!");
    foodId = Target.PromptTarget("Target a food")

if "picking" in order and skillStatus("Lockpicking") == 0:
    Player.HeadMessage(77, "!!! Target Training Lockbox !!!");
    lockedBox = Target.PromptTarget("Target training lockbox")

    lockPickId = 0x14FC
    lockPicks = Items.FindByID(int(lockPickId),0,mainpack.Serial,-1,False)

    if useOwnPicks == False:
        lockPicks = Target.PromptTarget("Target lockpicks")

if "removetrap" in order and skillStatus("Remove Trap") == 0:
    #----------Remove Trap heavily stolen from Pacho of Heritage server.  All credit goes to them.
    #   Increase this to see the gump getting solved, will make the puzzle time longer
    visual_delay = 1
    #   Lower this if you have a good connection.
    #   Will make the logs spam more with the message telling you to wait before using another skill
    timeout_delay = 1000

    Player.HeadMessage(77, "!!! Target Circuit Trap Kit !!!");
    trap_box = Target.PromptTarget("Target a circuit trap training kit")
    initial_skill = Player.GetRealSkillValue("Remove Trap")
   #------------------end Remove Trap vars



def remTrap():
    global runs
    global fails
    global avg_reset_time
    global last_puzzle_time
    global run_data
    global visual_delay
    global timeout_delay
    global trap_box
    global initial_skill
    global box_gump
    global up
    global down
    global left
    global right
    global messages

    box_gump = 653724266
    #box_gump = 1949253914
    up = 1
    right = 2
    down = 3
    left = 4
    messages = {
        "success":"You successfully disarm the trap!",
        "fail":"You fail to disarm the trap and reset it",
        "wait":"You must wait a few moments to use another skill"
    }
    run_data = {
        "coords": [0,0],
        "used_coords": [[0,0]],
        "size": 3,
        "good_steps": [],
        "incoming_dir": left,
        "last_dir": up,
        "successive_fails": 0,
        "time_started":datetime.now()
    }
    fails = 0
    runs = 1
    avg_reset_time = 0
    last_puzzle_time = 0



    # Resets the system
    def reset(data):
        data["coords"] = [0,0]
        data["used_coords"] = [[0,0]]
        data["size"] = 3
        data["good_steps"] = []
        data["incoming_dir"] = left
        data["last_dir"] = up
        data["successive_fails"] = 0
        data["time_started"] = datetime.now()
        if Gumps.HasGump():
            Gumps.CloseGump(box_gump)

    #   Get the next dir
    def getNextDir(last_dir, incoming_dir, cur_coords, used_coords, size, cycle=0):
        # Prevents recursion from happening too much.  It shouldn't recalculate enough to go around
        if cycle > 3:
            Misc.SendMessage("Recursion too deep! Aborting recalculation...", 0x80)
            return last_dir
        next_dir = (last_dir)%4 + 1
        if (next_dir == incoming_dir) or (next_dir == left and cur_coords[0] == 0) or (next_dir == up and cur_coords[1] == 0) or (next_dir == right and cur_coords[0] == (size-1)) or (next_dir == down and cur_coords[1] == (size-1)):
            next_dir = getNextDir(next_dir, incoming_dir, cur_coords, used_coords, size, cycle + 1)
        displacement = getDisplacement(next_dir)
        new_coords = [cur_coords[0] + displacement[0], cur_coords[1] + displacement[1]]
        coords_traveled = False
        for coord in used_coords:
            if coord[0] == new_coords[0] and coord[1] == new_coords[1]:
                coords_traveled = True
                break
        if coords_traveled:
            next_dir = getNextDir(next_dir, incoming_dir, cur_coords, used_coords, size, cycle + 1)
        if (cur_coords[0] == (size-1) and next_dir == up) or (cur_coords[1] == (size-1)and next_dir == left) or (cur_coords[0] == 0 and next_dir == left) or (cur_coords[1] == 0 and next_dir == up):
            #Misc.SendMessage("Wrong way: " + dirStr(next_dir) + " Size: " + str(size) + " Coords: " + str(cur_coords), 0x80)
            next_dir = getNextDir(next_dir, incoming_dir, cur_coords, used_coords, size, cycle + 1)
        return next_dir
    def getDisplacement(dir):
        if dir == up:
            return [0, -1]
        elif dir == right:
            return [1, 0]
        elif dir == down:
            return [0, 1]
        elif dir == left:
            return [-1, 0]
        else:
            return [0, 0]
    def getReverseDir(dir):
        if dir == up:
            return down
        elif dir == right:
            return left
        elif dir == down:
            return up
        elif dir == left:
            return right
    def dirStr(dir):
        if dir == up:
            return "up"
        elif dir == right:
            return "right"
        elif dir == down:
            return "down"
        elif dir == left:
            return "left"
        else:
            return "unknown: " + str(dir)
    ###
    def expMovingAvg(new_val, cur_avg, n):
        return (new_val - cur_avg)*(2/float(n+1))+cur_avg
    ###
    #Actual program
    reset(run_data)
    Journal.Clear()
    while Player.GetRealSkillValue("Remove Trap") < Player.GetSkillCap("Remove Trap") and skillStatus("Remove Trap") == 0:
        Target.Cancel()
        gains = Player.GetRealSkillValue("Remove Trap") - initial_skill
        #Misc.SendMessage("Skill: " + str("{0:.1f}".format(Player.GetRealSkillValue("Remove Trap"))) + " Skillgain since start: " + str("{0:.1f}".format(gains)), 0x60)
        #Misc.SendMessage("Runs: " + str(runs) + " Fails: " + str(fails), 0x80)
        #Misc.SendMessage(" Avg fails/run: " + str("{0:.1f}".format((0.0+fails)/runs), 0x80))
        #Misc.SendMessage(" Avg skillgain/run: " + str("{0:.1f}".format(gains/runs)), 0x80)
        #Misc.SendMessage(" Avg puzzle time: " + str(avg_reset_time), 0x80)
        Player.UseSkill("Remove Trap")
        Target.WaitForTarget(timeout_delay, False)
        while Journal.Search(messages["wait"]):
            Journal.Clear()
            Player.UseSkill("Remove Trap")
            Misc.Pause(visual_delay)
            Target.WaitForTarget(timeout_delay, False)
        Target.TargetExecute(trap_box)
        Gumps.WaitForGump(box_gump, timeout_delay)
        Misc.Pause(visual_delay)
        Journal.Clear()
        if not Gumps.HasGump():
            Target.Cancel()
            continue
        gump_data = Gumps.LastGumpRawData()
        # Count of grey points that are possible to traverse.  Used to get the board size instead of a skill level
        midpoint_count = gump_data.count("9720")
        # 3x3 has 7 midpoints
        if midpoint_count == 7:
            run_data["size"] = 3
        else:
            run_data["size"] = 4
        if run_data["size"] == 0:
            Misc.SendMessage("Puzzle size indeterminate, stopping script", 0x110)
            break
        Misc.SendMessage("Puzzle Size: " + str(run_data["size"]), 0x60)
        # Executes all known good steps for this box run
        Misc.SendMessage("Executing known steps: " + str(map(lambda x : dirStr(x), run_data["good_steps"])), 0x80)
        Misc.SendMessage("Used coords: " + str(run_data["used_coords"]), 0x80)
        for step in run_data["good_steps"]:
            Gumps.SendAction(box_gump, step)
            Gumps.WaitForGump(box_gump, timeout_delay)
            Misc.Pause(visual_delay)

        while not (Journal.Search(messages["success"]) or Journal.Search(messages["fail"])):
            run_data["next_dir"] = getNextDir(run_data["last_dir"], run_data["incoming_dir"], run_data["coords"], run_data["used_coords"], run_data["size"])
            Misc.SendMessage("Trying " + dirStr(run_data["next_dir"]) + ", previous try " + dirStr(run_data["last_dir"]) + ", came from " + dirStr(run_data["incoming_dir"]), 0x49)
            Gumps.SendAction(box_gump, run_data["next_dir"])
            Gumps.WaitForGump(box_gump, timeout_delay)
            run_data["last_dir"] = run_data["next_dir"]
            if Gumps.HasGump():
                displacement = getDisplacement(run_data["last_dir"])
                run_data["coords"] = [run_data["coords"][0] + displacement[0],run_data["coords"][1] + displacement[1]]
                run_data["good_steps"].append(run_data["last_dir"])
                run_data["used_coords"].append([run_data["coords"][0], run_data["coords"][1]])
                run_data["incoming_dir"] = getReverseDir(run_data["last_dir"])
                run_data["successive_fails"] = 0
                Misc.Pause(visual_delay)
            else:
                break
        if Journal.Search(messages["success"]):
            Misc.SendMessage("Succeeded", 0x39)
            runs = runs + 1
            last_puzzle_time = datetime.now() - run_data["time_started"]
            avg_reset_time = expMovingAvg(last_puzzle_time.total_seconds(), avg_reset_time, runs-1)
            Misc.SendMessage("Solve time: " + str(last_puzzle_time), 0x39)
            reset(run_data)
        elif Journal.Search(messages["fail"]):
            Misc.SendMessage("Failed", 0x39)
            run_data["successive_fails"] = run_data["successive_fails"]+1
            fails = fails + 1
            if run_data["successive_fails"] > 3:
                Misc.SendMessage("Too many successive fails, resetting...", 0x80)
                if Gumps.HasGump():
                    Gumps.CloseGump(box_gump)
                reset(run_data)
        else:
            Misc.SendMessage("Timed out", 0x39)
    Misc.SendMessage("Training complete!", 0x90)


def barker(skillName, initialSkill):
    gains = Player.GetRealSkillValue(skillName) - initialSkill
    gains = str("{0:.1f}".format(gains))
    skillValue = round(Player.GetRealSkillValue(skillName), 2)
    skillValue = str("{0:.1f}".format(skillValue))
    Misc.SendMessage("Skill: " + str(skillValue) +"\n" + "Skillgain since start: " + str(gains), 0x50)

def armsLore():
    skillName = "Arms Lore"
    initialSkill = Player.GetRealSkillValue(skillName)
    while Player.GetSkillCap(skillName) > Player.GetSkillValue(skillName) and skillStatus(skillName) == 0:
        barker(skillName, initialSkill)
        Player.UseSkill(skillName)
        Target.WaitForTarget(shortPause, False)
        Target.TargetExecute(weaponId)
        Misc.Pause(shortPause)
    Misc.SendMessage("All done with " + str(Player.GetRealSkillValue(skillName)) + "!.", 0x60)

def healing():
    skillName = "Healing"
    bandages = Items.FindByID(0x0E21, 0, Player.Backpack.Serial)
    bandageCount = Items.BackpackCount(0x0E21, 0);
    initialSkill = Player.GetRealSkillValue(skillName)
    while bandageCount > 0 and Player.GetSkillCap(skillName) > Player.GetSkillValue(skillName) and skillStatus(skillName) == 0:
        barker(skillName, initialSkill)
        Items.Move(hitPointArmor, 0x4046DCDA, 1)
        Misc.Pause(2000)
        Player.EquipItem(hitPointArmor)
        Misc.Pause(2000)
        Items.UseItem(bandages,Player.Serial)
        Misc.Pause(4000)
        bandageCount = Items.BackpackCount(0x0E21, 0);
    Misc.SendMessage("All done with " + str(Player.GetRealSkillValue(skillName)) + "!.", 0x60)

def anatomy():
    skillName = "anatomy"
    if not Player.IsGhost and Player.GetRealSkillValue(skillName) < Player.GetSkillCap(skillName) and skillStatus(skillName) == 0:
        Timer.Create( 'anatomyTimer', 1 )
        targetStillExists = Mobiles.FindBySerial( anatomyTarget )
        anatomyTimerMilliseconds = 4200
        initialSkill = Player.GetRealSkillValue(skillName)
        while targetStillExists != None and not Player.IsGhost and Player.GetRealSkillValue(skillName) < Player.GetSkillCap(skillName) and skillStatus(skillName) == 0:
            barker(skillName, initialSkill)
            if not Timer.Check( 'anatomyTimer' ):
                Player.UseSkill(skillName)
                Target.WaitForTarget( 2000, True )
                Target.TargetExecute( anatomyTarget )
                Timer.Create( 'anatomyTimer', anatomyTimerMilliseconds )
            Misc.Pause( shortPause )
            targetStillExists = Mobiles.FindBySerial( anatomyTarget )
        if targetStillExists == None:
            Player.HeadMessage(77, '!!! Selected target for anatomy is gone !!!');
        elif Player.GetRealSkillValue(skillName) >= Player.GetSkillCap(skillName):
            Player.HeadMessage( 77, '!!! Anatomy training complete !!!' )
        Misc.SendMessage("All done with " + str(Player.GetRealSkillValue(skillName)) + "!.", 0x60)

def animallore():
    skillName = "animal lore"
    if not Player.IsGhost and Player.GetRealSkillValue(skillName) < Player.GetSkillCap(skillName) and skillStatus(skillName) == 0:
        Timer.Create( 'loreTimer', 1 )
        targetStillExists = Mobiles.FindBySerial( veterinaryTarget )
        loreTimerMilliseconds = 4200
        initialSkill = Player.GetRealSkillValue(skillName)
        while targetStillExists != None and not Player.IsGhost and Player.GetRealSkillValue(skillName) < Player.GetSkillCap(skillName) and skillStatus(skillName) == 0:
            barker(skillName, initialSkill)
            if not Timer.Check( 'loreTimer' ):
                Player.UseSkill(skillName)
                Target.WaitForTarget( 2000, True )
                Target.TargetExecute( veterinaryTarget )
                Timer.Create( 'loreTimer', loreTimerMilliseconds )
            Misc.Pause( shortPause )
            Gumps.SendAction(3644314075, 0)
            targetStillExists = Mobiles.FindBySerial( veterinaryTarget )
        if targetStillExists == None:
            Player.HeadMessage(77, '!!! Selected target for animal lore is gone !!!');
        elif Player.GetRealSkillValue(skillName) >= Player.GetSkillCap(skillName):
            Player.HeadMessage( 77, '!!! animal lore training complete !!!' )
        Misc.SendMessage("All done with " + str(Player.GetRealSkillValue(skillName)) + "!.", 0x60)

def begging():
    skillName = "Begging"
    if not Player.IsGhost and Player.GetSkillValue(skillName) < Player.GetSkillCap(skillName) and skillStatus(skillName) == 0:
        Timer.Create( 'beggingTimer', 1 )
        targetStillExists = Mobiles.FindBySerial( beggingTarget )
        beggingTimerMilliseconds = 13000
        initialSkill = Player.GetSkillValue(skillName)
        while targetStillExists != None and not Player.IsGhost and Player.GetSkillValue(skillName) < Player.GetSkillCap(skillName) and skillStatus(skillName) == 0:
            Player.HeadMessage(77, str(Player.GetSkillValue(skillName)));
            barker(skillName, initialSkill)
            if not Timer.Check( 'beggingTimer' ):
                Player.UseSkill(skillName)
                Target.WaitForTarget( 2000, True )
                Target.TargetExecute( beggingTarget )
                Timer.Create( 'beggingTimer', beggingTimerMilliseconds )
            Misc.Pause( shortPause )
            targetStillExists = Mobiles.FindBySerial( beggingTarget )
        if targetStillExists == None:
            Player.HeadMessage(77, '!!! Selected target for begging is gone !!!');
        elif Player.GetSkillValue(skillName) >= Player.GetSkillCap(skillName):
            Player.HeadMessage( 77, '!!! begging training complete !!!' )
        Misc.SendMessage("All done with " + str(Player.GetSkillValue(skillName)) + "!.", 0x60)

def evalint():
    skillName = "Evaluating Intelligence"
    if not Player.IsGhost and Player.GetRealSkillValue(skillName) < Player.GetSkillCap(skillName) and skillStatus(skillName) == 0:
        Timer.Create( 'anatomyTimer', 1 )
        targetStillExists = Mobiles.FindBySerial( anatomyTarget )
        anatomyTimerMilliseconds = 4200
        initialSkill = Player.GetRealSkillValue(skillName)
        while targetStillExists != None and not Player.IsGhost and Player.GetRealSkillValue(skillName) < Player.GetSkillCap(skillName) and skillStatus(skillName) == 0:
            barker(skillName, initialSkill)
            if not Timer.Check( 'anatomyTimer' ):
                Player.UseSkill(skillName)
                Target.WaitForTarget( 2000, True )
                Target.TargetExecute( anatomyTarget )
                Timer.Create( 'anatomyTimer', anatomyTimerMilliseconds )
            Misc.Pause( shortPause )
            targetStillExists = Mobiles.FindBySerial( anatomyTarget )
        if targetStillExists == None:
            Player.HeadMessage(77, '!!! Selected target for evailint is gone !!!');
        elif Player.GetRealSkillValue(skillName) >= Player.GetSkillCap(skillName):
            Player.HeadMessage( 77, '!!! Evaluating Int training complete !!!' )
        Misc.SendMessage("All done with " + str(Player.GetRealSkillValue(skillName)) + "!.", 0x60)


def itemId():
    skillName = "Item ID"
    initialSkill = Player.GetRealSkillValue(skillName)
    while Player.GetSkillCap(skillName) > Player.GetSkillValue(skillName) and skillStatus(skillName) == 0:
        barker(skillName, initialSkill)
        Player.UseSkill(skillName)
        Target.WaitForTarget(shortPause, False)
        Target.TargetExecute(weaponId)
        Misc.Pause(shortPause)
    Misc.SendMessage("All done with " + str(Player.GetRealSkillValue(skillName)) + "!.", 0x60)

def tasteId():
    skillName = "Taste ID"
    initialSkill = Player.GetRealSkillValue(skillName)
    while Player.GetSkillCap(skillName) > Player.GetSkillValue(skillName) and skillStatus(skillName) == 0:
        barker(skillName, initialSkill)
        Player.UseSkill(skillName)
        Target.WaitForTarget(shortPause, False)
        Target.TargetExecute(foodId)
        Misc.Pause(shortPause)
    Misc.SendMessage("All done with " + str(Player.GetRealSkillValue(skillName)) + "!.", 0x60)

def detectHidden():
    skillName = "Detect Hidden"
    initialSkill = Player.GetRealSkillValue(skillName)
    while Player.GetSkillCap(skillName) > Player.GetSkillValue(skillName) and skillStatus(skillName) == 0:
        barker(skillName, initialSkill)
        Player.UseSkill(skillName)
        Target.WaitForTarget(shortPause, False)
        Target.Self()
        Misc.Pause(shortPause)
    Misc.SendMessage("All done with " + str(Player.GetRealSkillValue(skillName)) + "!.", 0x60)

def hiding():
    skillName = "Hiding"
    initialSkill = Player.GetRealSkillValue(skillName)
    while Player.GetSkillCap(skillName) > Player.GetSkillValue(skillName) and skillStatus(skillName) == 0:
        barker(skillName, initialSkill)
        Player.UseSkill(skillName)
        Misc.Pause(longPause)
    Misc.SendMessage("All done with " + str(Player.GetRealSkillValue(skillName)) + "!.", 0x60)


def spirit():
    skillName = "Spirit Speak"
    initialSkill = Player.GetRealSkillValue(skillName)
    while Player.GetSkillCap(skillName) > Player.GetSkillValue(skillName) and skillStatus(skillName) == 0:
        barker(skillName, initialSkill)
        Player.UseSkill(skillName)
        Misc.Pause(longPause)
    Misc.SendMessage("All done with " + str(Player.GetRealSkillValue(skillName)) + "!.", 0x60)

def lockPicking():
    skillName = "Lockpicking"
    initialSkill = Player.GetRealSkillValue(skillName)
    while Player.GetSkillCap(skillName) > Player.GetSkillValue(skillName) and skillStatus(skillName) == 0:
        barker(skillName, initialSkill)
        if useOwnPicks == True:
            lockPickCount = Items.BackpackCount(lockPickId,-1)
            if lockPickCount < 1:
                Misc.SendMessage("Ran out of lockpicks.  Moving on to next skill", 0x60)
                break

        Items.UseItem(lockedBox)
        Misc.Pause(500)
        Items.UseItem(lockPicks)
        Target.WaitForTarget(500, False)
        Target.TargetExecute(lockedBox)
        Misc.Pause(500)

def camping():
    skillName = "camping"
    initialSkill = Player.GetRealSkillValue(skillName)
    while Player.GetSkillCap(skillName) > Player.GetSkillValue(skillName) and skillStatus(skillName) == 0:
        barker(skillName, initialSkill)
        kindlingCount = Items.BackpackCount(kindlingId,-1)
        if kindlingCount < 1:
            Misc.SendMessage("Ran out of kindling.  Moving on to next skill", 0x60)
            break
        Items.UseItem(kindling)
        Misc.Pause(shortPause)

def tracking():
    skillName = "Tracking"
    gumpID = 2976808305;
    #gumpID = 3505039983;
    initialSkill = Player.GetRealSkillValue(skillName)
    while Player.GetSkillCap(skillName) > Player.GetSkillValue(skillName) and skillStatus(skillName) == 0:
        barker(skillName, initialSkill)
        Player.UseSkill(skillName)
        Gumps.WaitForGump(gumpID,10000)
        Gumps.SendAction(gumpID,3)
        Gumps.CloseGump(gumpID)
        Misc.Pause(longPause)

def spellweaving():
    skillName = "Spell Weaving"
    initialSkill = Player.GetRealSkillValue(skillName)
    while Player.GetSkillCap(skillName) > Player.GetRealSkillValue(skillName) and skillStatus(skillName) == 0:
        barker(skillName, initialSkill)
        skillLevel = Player.GetRealSkillValue(skillName)

        if Player.Mana < 25:
            Player.UseSkill('meditation')
            while Player.Mana < Player.ManaMax:
                Player.UseSkill('meditation')
                Misc.Pause(2000)

        if skillLevel < 20 and Player.Mana > 20:
            Spells.CastSpellweaving('Arcane Circle')
            Misc.Pause(2000)

        if skillLevel >= 20 and skillLevel < 36 and Player.Mana > 20:
            Spells.CastSpellweaving('Immolating Weapon')
            Misc.Pause(2200)

        if skillLevel >= 36 and skillLevel < 58  and Player.Mana > 40:
            Spells.CastSpellweaving('Reaper Form')
            Misc.Pause(4000)

        if skillLevel >= 58 and skillLevel < 74  and Player.Mana > 60:
            Spells.CastSpellweaving('Essence Of Wind')
            Misc.Pause(5000)

        if skillLevel >= 74 and skillLevel < 92  and Player.Mana > 60:
            Spells.CastSpellweaving('Wildfire')
            Target.WaitForTarget(4000,False)
            Target.Self()
            Misc.Pause(5000)

        if skillLevel >= 92 and skillLevel != Player.GetSkillCap(skillName) and Player.Mana > 60:
            if Player.Hits < 50:
                Spells.CastSpellweaving('Gift Of Renewal')
                Target.WaitForTarget(4000,False)
                Target.Self()
                Misc.Pause(2000)
            else:
                Spells.CastSpellweaving('Word Of Death')
                Target.WaitForTarget(4000,False)
                Target.Self()
            Misc.Pause(2000)
    Misc.SendMessage("All done with " + str(Player.GetRealSkillValue(skillName)) + "!.", 0x60)


def necro():
    skillName = "Necromancy"
    initialSkill = Player.GetRealSkillValue(skillName)
    while Player.GetSkillCap(skillName) > Player.GetRealSkillValue(skillName) and skillStatus(skillName) == 0:
        barker(skillName, initialSkill)
        skillLevel = Player.GetRealSkillValue(skillName)

        if Player.Mana < 25:
            Player.UseSkill('meditation')
            while Player.Mana < Player.ManaMax:
                Player.UseSkill('meditation')
                Misc.Pause(2000)

        # if skillLevel > 0 and skillLevel < 40:
        #     Spells.CastNecro('')

        if skillLevel >= 0 and skillLevel < 55:
            Spells.CastNecro('Pain Spike')
            Target.WaitForTarget(4000,False)
            Target.Self()

        if skillLevel >= 55 and skillLevel < 70:
            Spells.CastNecro('Horrific Beast')
            Target.WaitForTarget(4000,False)
            Target.Self()

        if skillLevel >= 70 and skillLevel < 85:
            # check if in horrific beast form, cast again to leave form to continue
            if Player.BuffsExist('Horrific Beast'):
                Misc.Pause (400)
                Spells.CastNecro("Horrific Beast")
                Misc.Pause(3500)
            else:
                Spells.CastNecro('Wither')
                Target.WaitForTarget(4000,False)
                Target.Self()

        if skillLevel >= 85 and skillLevel < 100:
            Spells.CastNecro('Lich Form')
            Target.WaitForTarget(4000,False)
            Target.Self()

        if skillLevel >= 100 and skillLevel < 120:
            Spells.CastNecro('Vampiric Embrace')

        Misc.Pause(2500)
    Misc.SendMessage("All done with " + str(Player.GetRealSkillValue(skillName)) + "!.", 0x60)



def magery():
    skillName = "Magery"
    initialSkill = Player.GetRealSkillValue(skillName)
    while Player.GetSkillCap(skillName) > Player.GetRealSkillValue(skillName) and skillStatus(skillName) == 0:
        barker(skillName, initialSkill)
        skillLevel = Player.GetRealSkillValue(skillName)

        if Player.Mana < 25:
            Player.UseSkill('meditation')
            while Player.Mana < Player.ManaMax:
                Player.UseSkill('meditation')
                Misc.Pause(2000)

        # if skillLevel > 0 and skillLevel < 30:
        #     Spells.CastMagery('')

        if skillLevel >= 30 and skillLevel < 55:
            Spells.CastMagery('Mana Drain')
            Target.WaitForTarget(4000,False)
            Target.Self()

        if skillLevel >= 55 and skillLevel < 70:
            Spells.CastMagery('Paralyze')
            Target.WaitForTarget(4000,False)
            Target.Self()

        if skillLevel >= 70 and skillLevel < 90:
            Spells.CastMagery('Mana Vampire')
            Target.WaitForTarget(4000,False)
            Target.Self()

        if skillLevel >= 90 and skillLevel < 120:
            Spells.CastMagery('earthquake')

        Misc.Pause(3500)
    Misc.SendMessage("All done with " + str(Player.GetRealSkillValue(skillName)) + "!.", 0x60)


def chivalry():
    skillName = "Chivalry"
    initialSkill = Player.GetRealSkillValue(skillName)
    while Player.GetSkillCap(skillName) > Player.GetRealSkillValue(skillName) and skillStatus(skillName) == 0:
        barker(skillName, initialSkill)
        skillLevel = Player.GetRealSkillValue(skillName)

        if Player.Mana < 20:
            Player.UseSkill('meditation')
            while Player.Mana < Player.ManaMax:
                Player.UseSkill('meditation')
                Misc.Pause(2000)

        # if skillLevel > 0 and skillLevel < 30:
        #     Spells.CastChivalry('')

        if skillLevel >= 0 and skillLevel < 45:
            Spells.CastChivalry('Consecrate Weapon')
            Target.WaitForTarget(4000,False)
            Target.Self()

        if skillLevel >= 45 and skillLevel < 60:
            Spells.CastChivalry('Divine Fury')

        if skillLevel >= 60 and skillLevel < 70:
            Spells.CastChivalry('Enemy of One')

        if skillLevel >= 70 and skillLevel < 90:
            Spells.CastChivalry('Holy Light')

        if skillLevel >= 90 and skillLevel < 120:
            Spells.CastChivalry('Noble Sacrifice')

        Misc.Pause(2500)
    Misc.SendMessage("All done with " + str(Player.GetRealSkillValue(skillName)) + "!.", 0x60)


def BandageTarget():
    lastTarget = Target.GetLast()
    while Target.HasTarget():
        Misc.Pause(10)
    Items.UseItemByID(0x0E21, 0)
    Target.WaitForTarget(1500, False)
    Target.TargetExecute( lastTarget )
    Misc.Pause (500)
    Target.SetLast(lastTarget)
    Target.TargetExecute( lastTarget )

# Created by Balandar
def vet():
    skillName = "Veterinary"
    if not Player.IsGhost and Player.GetSkillValue(skillName) < Player.GetSkillCap(skillName) and skillStatus(skillName) == 0:
        Player.HeadMessage( 1100, '!! Starting Veterinary !' )
        initialSkill = Player.GetRealSkillValue(skillName)
        #Player.HeadMessage(77, str(Player.GetSkillValue(skillName)));
        Timer.Create( 'vetTimer', 1 )
        targetStillExists = Mobiles.FindBySerial( veterinaryTarget )
        vetTimerMilliseconds = 13000
        initialSkill = Player.GetSkillValue(skillName)
        while targetStillExists != None and not Player.IsGhost and Player.GetSkillValue(skillName) < Player.GetSkillCap(skillName) and skillStatus(skillName) == 0:
            halfHits = int(targetStillExists.HitsMax / 2)
            #Player.HeadMessage(77, str(Player.GetSkillValue(skillName)));
            barker(skillName, initialSkill)
            if targetStillExists.Hits < halfHits:
                Player.HeadMessage( 1100, 'Stop Attacking!' )
                Player.SetWarMode(False)
            if not Timer.Check( 'vetTimer' ):
                if Items.BackpackCount( 0x0E21 ,-1 ):
                    if targetStillExists.Visible == True and targetStillExists.Hits < targetStillExists.HitsMax or targetStillExists.Poisoned:
                        Target.SetLast(veterinaryTarget)
                        BandageTarget()
                    elif targetStillExists.Hits > halfHits:
                        Player.HeadMessage( 1100, 'Attacking!' )
                        Player.SetWarMode(True)
                        Player.Attack(targetStillExists)
                else:
                    Player.HeadMessage( 1100, 'Out of bandages!' )
                Timer.Create( 'vetTimer', vetTimerMilliseconds )

            Misc.Pause( shortPause )
            targetStillExists = Mobiles.FindBySerial( veterinaryTarget )
            if targetStillExists.Hits < halfHits:
                Player.HeadMessage( 1100, 'Stop Attacking!' )
                Player.SetWarMode(False)
        if targetStillExists == None:
            Player.HeadMessage(77, '!!! Selected target for Veterinary is gone !!!');
        elif Player.GetSkillValue(skillName) >= Player.GetSkillCap(skillName):
            Player.HeadMessage( 77, '!!! Veterinary training complete !!!' )
        Misc.SendMessage("All done with " + str(Player.GetSkillValue(skillName)) + "!.", 0x60)
        Player.HeadMessage( 1100, 'Stop Attacking!' )
        Player.SetWarMode(False)
    Misc.SendMessage("All done with " + str(Player.GetRealSkillValue(skillName)) + "!.", 0x60)

def main(skillList):
    for skill in skillList:
        if skill == "arms":
            armsLore()
        if skill == "item":
            itemId()
        if skill == "taste":
            tasteId()
        if skill == "detect":
            detectHidden()
        if skill == "hide":
            hiding()
        if skill == "removetrap":
            remTrap()
        if skill == "picking":
            lockPicking()
        if skill == "camp":
            camping()
        if skill == "tracking":
            tracking()
        if skill == "spirit":
            spirit()
        if skill == "spellweaving":
            spellweaving()
        if skill == "necro":
            necro()
        if skill == "magery":
            magery()
        if skill == "chivalry":
            chivalry()
        if skill == "anatomy":
            anatomy()
        if skill == "beg":
            begging()
        if skill == "vet":
            vet()
        if skill == "animallore":
            animallore()
        if skill == "healing":
            healing()
        if skill == "evalint":
            evalint()



main(order)
