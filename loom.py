order = ["thread","yarn"]

threadID = 0x0FA0
yarnID = 0x0E1D

Loom = Target.PromptTarget( 'Select loom to use' )

def loomThat(itemID):
    loomItem = Items.FindByID(itemID, 0, Player.Backpack.Serial)
    if loomItem:
        loomItemCount = Items.BackpackCount(itemID, 0);
        while loomItemCount > 0:
            Misc.SendMessage(loomItemCount, 0x60)
            Items.UseItem(loomItem)
            Target.WaitForTarget(500, False)
            Target.TargetExecute(Loom)
            Misc.Pause(500)
            loomItemCount = Items.BackpackCount(itemID, 0);
        Misc.SendMessage("All done with Looming!.", 0x60)


def main(itemList):
    for item in itemList:
        if item == "thread":
            loomThat(threadID)
        if item == "yarn":
            loomThat(yarnID)

main(order)