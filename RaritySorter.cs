using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using System.Text.RegularExpressions;
using RazorEnhanced;

namespace RazorScripts
{

    public class RaritySorter
    {
        List<SortRule> _rules = new List<SortRule>();

        public void Run()
        {
            var tar = new Target();
            var raities = Enum.GetValues(typeof(ItemRarity)).Cast<ItemRarity>().ToList();

            // Set value of bag serials here if you always use the same ones. Otherwise set to -1
            Dictionary<string, int> bags =
                    new Dictionary<string, int>(){
                                        {"MinorMagicItem", -1},
                                        {"LesserMagicItem", -1},
                                        {"GreaterMagicItem", -1},
                                        {"MajorMagicItem", -1},
                                        {"MinorArtifact", -1},
                                        {"LesserArtifact", -1},
                                        {"GreaterArtifact", -1},
                                        {"MajorArtifact", -1},
                                        {"LegendaryArtifact", -1}
                                        };
            var sourceBag = tar.PromptTarget("Pick bag you wish to sort");

            if (sourceBag != -1)
            {
                var source = Items.FindBySerial(sourceBag);
                if (!source.IsContainer)
                {
                    Player.HeadMessage(33, "That s Not a suitable source");
                }

                if (!source.Contains.Any(i => i.IsLootable))
                {
                    Player.HeadMessage(33, "That bag is empty");
                }

                foreach (var rarity in raities)
                {
                    var rarityName = SplitCamelCase(rarity.ToString());
                    var targetSerial = -1;
                    var value = -1;
                    bool hasValue = bags.TryGetValue(rarity.ToString(), out value);
                    Misc.SendMessage($"{rarityName} exists: {hasValue}", 0x60);
                    if (hasValue && value != -1) {
                        targetSerial = value;
                    } else {
                        targetSerial = tar.PromptTarget($"Pick a bag for {rarityName}");
                    }
                    Misc.SendMessage($"{rarityName} serial: {targetSerial}", 0x60);
                    if (targetSerial != -1)
                    {
                        _rules.Add(new SortRule
                        {
                            TaretBag = Items.FindBySerial(targetSerial),
                            Rarity = rarity
                        });
                    }
                }

                Misc.SendMessage("Starting Sort Cycle", 0x99);

                foreach (var item in source.Contains.Where(i => i.IsLootable))
                {
                    Items.WaitForProps(item, 1000);
                    var rarityProp = item.Properties.FirstOrDefault(p => p.Number == 1042971);
                    if (rarityProp == null)
                    {
                        continue;
                    }

                    foreach (var rule in _rules)
                    {
                        //Find text between > and < and remove spaces
                        var rarityString = "";
                        var cleaned = rarityProp.Args.Substring(rarityProp.Args.IndexOf(">", StringComparison.Ordinal) + 1).Replace(" ", "");
                        var length = cleaned.IndexOf("<", StringComparison.Ordinal);
                        if (length == -1)
                        {
                            rarityString = cleaned.Substring(0);
                        }
                        else
                        {
                            rarityString = cleaned.Substring(0, cleaned.IndexOf("<", StringComparison.Ordinal));
                        }


                        var matched = rarityString.Equals(rule.Rarity.ToString(), StringComparison.OrdinalIgnoreCase);
                        if (matched)
                        {
                            Items.Move(item.Serial, rule.TaretBag.Serial, item.Amount);
                            Misc.Pause(200);
                        }
                    }
                }

                Misc.SendMessage("Sorting Complete", 0x99);

            }


        }

        public string SplitCamelCase(string str)
        {
            return Regex.Replace(
                Regex.Replace(
                    str,
                    @"(\P{Ll})(\P{Ll}\p{Ll})",
                    "$1 $2"
                ),
                @"(\p{Ll})(\P{Ll})",
                "$1 $2"
            );
        }


    }

    internal class SortRule
    {
        public Item TaretBag { get; set; }
        public ItemRarity Rarity { get; set; }
    }

    internal enum ItemRarity
    {
        MinorMagicItem = 0,
        LesserMagicItem = 1,
        GreaterMagicItem = 2,
        MajorMagicItem = 3,
        MinorArtifact = 4,
        LesserArtifact = 5,
        GreaterArtifact = 6,
        MajorArtifact = 7,
        LegendaryArtifact = 8
    }
}