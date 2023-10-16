
order = ["wool","cotton"]

woolID = 0x0DF8
cottonID = 0x0DF9

spinningWheel = Target.PromptTarget( 'Select spinningWheel to use' )

def spinThat(itemID):
    spinItem = Items.FindByID(itemID, 0, Player.Backpack.Serial)
    if spinItem:
        spinItemCount = Items.BackpackCount(itemID, 0);
        while spinItemCount > 0:
            Misc.SendMessage(spinItemCount, 0x60)
            Items.UseItem(spinItem)
            Target.WaitForTarget(500, False)
            Target.TargetExecute(spinningWheel)
            Misc.Pause(7500)
            spinItemCount = Items.BackpackCount(itemID, 0);
        Misc.SendMessage("All done with Spinning!.", 0x60)


def main(itemList):
    for item in itemList:
        if item == "wool":
            spinThat(woolID)
        if item == "cotton":
            spinThat(cottonID)


main(order)