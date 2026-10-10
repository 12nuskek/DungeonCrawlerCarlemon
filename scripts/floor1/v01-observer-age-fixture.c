/* Appended to unchanged native-event/observer unit harnesses. Entirely synthetic.
 * Captures use the existing no-output stub; there is no emulator or Save state. */
static void observe_native_pose(unsigned pose)
{
    active();
    v.candidate = 1;
    memcpy(ram + v.a.poseState - 0x02000000, sDccBattlePoses, 16);
    memcpy(v.poses[pose], sDccPosePictures[pose], 2048);
    memcpy(vram + 2048, buffers[1], 2048);
    memcpy(ram + BUFFER - 0x02000000 + 8192, buffers[1], 8192);
    put8(0x02001890, gAnimScriptActive);
    put8(0x02001891, gBattleAnimAttacker);
}

int main(void)
{
    unsigned cases = 0;
    for (unsigned trainer = 858; trainer <= 859; trainer++) {
        native_setup(trainer);
        start(1, 359);
        step(17);
        assert(sDccBattlePoses[1].action == WINDUP && sDccBattlePoses[1].age == 17);
        assert(sDccPoseActive & 2);
        observe_native_pose(14);
        assert(!sample() && !v.warningFrames);
        cases++;

        step(1);
        assert(sDccBattlePoses[1].age == 18 && !(sDccPoseActive & 2));
        observe_native_pose(14);
        assert(!sample() && v.warningFrames == 1);
        cases++;

        step(60);
        assert(sDccBattlePoses[1].age == 18 && sDccBattlePoses[1].applied == 15);
        observe_native_pose(14);
        assert(!sample() && v.warningFrames == 1);
        cases++;

        start(0, 356);
        step(1);
        assert(sDccBattlePoses[1].age >= 18 && !(sDccPoseActive & 2));
        observe_native_pose(14);
        assert(!sample() && v.warningOtherActor == 1);
        cases++;

        memset(vram + 2048, 22, 2048); /* Existing harness pose12 pattern, wrong held warning. */
        assert(sample() == 108 && v.failedStage == 5);
        cases++;

        start(1, 360);
        step(1);
        DccBattlePoseImpact();
        step(13);
        assert(sDccBattlePoses[1].action == REST && sDccBattlePoses[1].applied == 13);
        assert(!(sDccPoseActive & 2));
        unsigned rest_age = sDccBattlePoses[1].age;
        step(60);
        assert(sDccBattlePoses[1].age == rest_age);
        observe_native_pose(12);
        assert(!sample() && !v.warningFrames);
        cases++;
    }
    active();
    v.candidate = 1;
    put32(PHASE, v.a.freeReset);
    put32(v.a.gfx, 0);
    put8(v.a.poseState + 5, 1); /* Synthetic stale age: retirement must still fail. */
    assert(sample() == 105 && v.failedStage == 10);
    cases++;
    DccBattlePoseReset();
    assert(!sDccPoseActive && !sDccPosePending);
    memcpy(ram + v.a.poseState - 0x02000000, sDccBattlePoses, 16);
    assert(!sample() && v.lifecycle == BV_RETIRING);
    return_path();
    assert(!sample() && v.lifecycle == BV_FIELD && v.exitClean == 1);
    cases++;
    assert(cases == 14);
    puts("PASS source/observer age integration: 14 cases; no emulator, Save, reference stream or captures");
    return 0;
}
