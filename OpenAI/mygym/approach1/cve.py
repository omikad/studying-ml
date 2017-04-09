class Cve:
    Idea_Names = [' ', '&', '#', 'O', '.', '+']
    Vector_Names = ["Left", "Up", "Right", "Down", "KeyLeft", "KeyUp", "KeyRight", "KeyDown", "KeyRestart"]
    IsGameVector = [False, False, False, False, True, True, True, True, True]
    Game_Vectors = [i for i in xrange(len(IsGameVector)) if IsGameVector[i]]
    Non_Game_Vectors = [i for i in xrange(len(IsGameVector)) if not IsGameVector[i]]

    def __init__(self, cause_idea, cause_point, vector, effect_idea, effect_point):
        self.cause_idea = cause_idea
        self.cause_point = cause_point
        self.vector = vector
        self.effect_idea = effect_idea
        self.effect_point = effect_point

    def __repr__(self):
        return "'{}' {} -> {} -> '{}' {}".format(Cve.Idea_Names[self.cause_idea],
                                                 self.cause_point,
                                                 Cve.Vector_Names[self.vector],
                                                 Cve.Idea_Names[self.effect_idea],
                                                 self.effect_point)
