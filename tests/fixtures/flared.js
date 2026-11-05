// Declaration keywords are gold; control flow remains terracotta.
class Repair {
  constructor(label) {
    this.label = label;
  }
}
const repair = new Repair("gold");
if (repair.label) console.log(repair.label);
